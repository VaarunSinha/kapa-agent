"""
Celery task: index repository into Chroma for the given GitHub installation.
Clone → run understanding (doc/frontend/backend buckets) → load all repo files → chunk → embed → persist.
"""
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from celery import shared_task
from django.conf import settings

from github.models import GitHubInstallation
from github.services import create_installation_token

logger = logging.getLogger(__name__)

DOCS_SUBDIR = "docs"
EXCLUDE_SUBDIRS = ["blog", "images", "static"]
CHUNK_SIZE = 512
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "text-embedding-3-large"

# Extensions to index (docs + code)
INDEX_EXTENSIONS = [".md", ".mdx", ".rst", ".txt", ".py", ".ts", ".tsx", ".js", ".jsx", ".css", ".json"]

# Exclude patterns for full-repo reader (no node_modules, build artifacts, etc.)
INDEX_EXCLUDE = [
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.git/**",
    "**/venv/**",
    "**/.venv/**",
    "**/.next/**",
    "**/build/**",
    "**/dist/**",
    "**/chroma_data/**",
    "**/blog/**",
    "**/images/**",
    "**/static/**",
]


def _clone_repo(owner: str, repo_name: str, installation_id: int, tmpdir: str) -> None:
    """Clone repo into tmpdir."""
    token = create_installation_token(installation_id)
    repo_url = f"https://x-access-token:{token}@github.com/{owner}/{repo_name}.git"
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, tmpdir],
        check=True,
        capture_output=True,
        timeout=120,
    )


def _build_path_to_bucket_map(raw_understanding: dict, tmpdir: str) -> list:
    """
    Build list of (path_prefix, bucket) from understanding directories, sorted by path length descending
    so longest match wins. Paths normalized to use / and to be repo-relative.
    """
    dirs = raw_understanding.get("directories") or []
    pairs = []
    for d in dirs:
        path = (d.get("path") or "").strip().replace("\\", "/")
        bucket = (d.get("bucket") or "other").strip().lower()
        if bucket not in ("documentation", "frontend", "backend", "other"):
            bucket = "other"
        if not path:
            continue
        if not path.endswith("/"):
            path = path + "/"
        pairs.append((path, bucket))
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    return pairs


def _bucket_for_path(file_path: str, path_to_bucket: list) -> str:
    """Return bucket for a repo-relative file path using the path→bucket list (longest prefix match).
    When no directory matches, use path-based heuristics to assign backend or frontend."""
    normalized = file_path.replace("\\", "/")
    for prefix, bucket in path_to_bucket:
        if normalized.startswith(prefix) or normalized.startswith(prefix.rstrip("/")):
            return bucket
    # Path-based fallback when understanding agent did not list this directory
    lower = normalized.lower()
    if lower.startswith("docs/") or "/docs/" in lower:
        return "other"
    if any(seg in lower for seg in ("/backend/", "backend/", "/agent/", "agent/", "/api/", "/server/", "server/")):
        return "backend"
    if any(lower.endswith(ext) for ext in (".py", ".go", ".java")) and "docs" not in lower:
        return "backend"
    if any(seg in lower for seg in ("/frontend/", "frontend/", "/app/", "/src/", "/components/", "components/")):
        return "frontend"
    if any(lower.endswith(ext) for ext in (".tsx", ".jsx", ".vue")):
        return "frontend"
    return "other"


@shared_task(bind=True, max_retries=3)
def index_installation_task(self, installation_id: int):
    """
    Clone repo, run understanding (with bucket per directory), load all repo files,
    chunk, assign repo-relative path and bucket per node, embed, persist to Chroma.
    Sets chroma_collection_name on installation and source_status to ready or failed.
    """
    try:
        inst = GitHubInstallation.objects.get(installation_id=installation_id)
    except GitHubInstallation.DoesNotExist:
        logger.warning("index_installation_task: installation_id=%s not found", installation_id)
        return

    owner = inst.owner or ""
    repo_name = inst.repository_name or ""
    if not owner or not repo_name:
        inst.source_status = "failed"
        inst.save(update_fields=["source_status"])
        logger.warning("index_installation_task: no owner/repo for installation_id=%s", installation_id)
        return

    persist_dir = getattr(settings, "CHROMA_PERSIST_DIR", None) or str(
        Path(settings.BASE_DIR) / "chroma_data"
    )
    os.makedirs(persist_dir, exist_ok=True)
    collection_name = f"installation_{installation_id}"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            _clone_repo(owner, repo_name, installation_id, tmpdir)
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            result.check_returncode()
            tree_input = result.stdout
            try:
                tree_result = subprocess.run(
                    ["tree", "--fromfile", "-"],
                    cwd=tmpdir,
                    input=tree_input,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                tree_text = tree_result.stdout if tree_result.returncode == 0 and tree_result.stdout else tree_input
            except (FileNotFoundError, subprocess.SubprocessError):
                tree_text = tree_input

            from agent.agents.understanding import generate_understanding_structured
            from llama_index.core import SimpleDirectoryReader
            from llama_index.core.node_parser import SentenceSplitter
            from llama_index.core import VectorStoreIndex, StorageContext
            from llama_index.embeddings.openai import OpenAIEmbedding
            from llama_index.vector_stores.chroma import ChromaVectorStore
            import chromadb

            # 1) Load a small doc sample for understanding and style only (not for indexing)
            docs_path = os.path.join(tmpdir, DOCS_SUBDIR)
            if not os.path.isdir(docs_path):
                docs_path = tmpdir
            sample_reader = SimpleDirectoryReader(
                input_dir=docs_path,
                exclude=[
                    "**/blog/**",
                    "**/images/**",
                    "**/static/**",
                    "**/blog",
                    "**/images",
                    "**/static",
                ],
                required_exts=[".md", ".mdx", ".rst", ".txt"],
                recursive=True,
            )
            sample_docs = sample_reader.load_data()
            sample_preview = ""
            sample_for_style = ""
            if sample_docs:
                sample_preview = "\n\n".join(
                    (getattr(d, "text", "") or str(d))[:1500] for d in sample_docs[:3]
                )
                sample_for_style = "\n\n---\n\n".join(
                    (getattr(d, "text", "") or str(d)) for d in sample_docs[:5]
                )

            # 2) Run understanding and get (markdown, raw_dict)
            understanding_md, understanding_raw = generate_understanding_structured(tree_text, sample_preview)
            inst.understanding = understanding_md
            inst.raw_tree = tree_text
            inst.understanding_directories = (understanding_raw or {}).get("directories") or []
            inst.save(update_fields=["understanding", "raw_tree", "understanding_directories"])

            if sample_for_style:
                from agent.agents.style import extract_style
                inst.style_md = extract_style(sample_for_style)
                inst.save(update_fields=["style_md"])

            path_to_bucket = _build_path_to_bucket_map(understanding_raw, tmpdir) if understanding_raw else []

            # 3) Load all repo files (docs + code) from repo root
            reader = SimpleDirectoryReader(
                input_dir=tmpdir,
                exclude=INDEX_EXCLUDE,
                required_exts=INDEX_EXTENSIONS,
                recursive=True,
            )
            documents = reader.load_data()

            if not documents:
                logger.info(
                    "index_installation_task: no documents to index for installation_id=%s",
                    installation_id,
                )

            splitter = SentenceSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )
            nodes = splitter.get_nodes_from_documents(documents)

            for node in nodes:
                meta = node.metadata or {}
                path = meta.get("file_path") or meta.get("file_name") or ""
                try:
                    if os.path.isabs(path):
                        abs_path = path
                    else:
                        abs_path = os.path.join(tmpdir, path)
                    rel_path = os.path.relpath(abs_path, tmpdir)
                except (ValueError, TypeError):
                    rel_path = path.replace("\\", "/") if path else "document"
                if not rel_path or rel_path.startswith(".."):
                    rel_path = path.replace("\\", "/") if path else "document"
                node.metadata["file_path"] = rel_path.replace("\\", "/")
                node.metadata["bucket"] = _bucket_for_path(rel_path, path_to_bucket)
                node.metadata.setdefault("section_heading", "")
                node.metadata.setdefault("document_type", "doc")

            # Build unique path -> bucket list for admin / debugging (indexed tree)
            path_to_bucket_seen = {}
            for node in nodes:
                meta = node.metadata or {}
                p = (meta.get("file_path") or "").replace("\\", "/")
                b = (meta.get("bucket") or "other").strip()
                if p:
                    path_to_bucket_seen[p] = b
            inst.indexed_paths = [{"path": p, "bucket": b} for p, b in sorted(path_to_bucket_seen.items())]

            embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL)
            client = chromadb.PersistentClient(path=persist_dir)
            try:
                client.delete_collection(name=collection_name)
            except Exception:
                pass
            chroma_collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)

        inst.chroma_collection_name = collection_name
        inst.source_status = "ready"
        inst.save(update_fields=["chroma_collection_name", "source_status", "indexed_paths"])
        logger.info(
            "index_installation_task: indexed installation_id=%s collection=%s",
            installation_id,
            collection_name,
        )
    except Exception as e:
        logger.exception(
            "index_installation_task: failed for installation_id=%s: %s",
            installation_id,
            e,
        )
        inst.source_status = "failed"
        inst.indexed_paths = []
        inst.save(update_fields=["source_status", "indexed_paths"])
        raise
