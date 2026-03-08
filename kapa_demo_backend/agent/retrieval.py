"""
Vector retrieval helper: load Chroma index by installation, query top_k=8, format nodes, cap ~2500 tokens.
Used by Research and Writer agents. Optional bucket filter restricts to documentation/backend/frontend.
"""
import logging
from pathlib import Path
from typing import List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

SIMILARITY_TOP_K = 8
MAX_CONTEXT_TOKENS = 2500
# Rough chars per token for truncation
CHARS_PER_TOKEN = 4


def get_retrieval_context(
    installation_id: int,
    query: str,
    top_k: int = SIMILARITY_TOP_K,
    max_tokens: int = MAX_CONTEXT_TOKENS,
    buckets: Optional[List[str]] = None,
) -> str:
    """
    Load Chroma index for the installation, run similarity search, return formatted context string.
    Format: "File: <path>\n\nContent:\n<chunk>". Total length capped at ~max_tokens (by chars).
    If buckets is non-empty, only nodes whose metadata bucket is in buckets are returned.
    Returns empty string if no installation/index or on error.
    """
    try:
        from github.models import GitHubInstallation
        from llama_index.core import VectorStoreIndex, StorageContext
        from llama_index.embeddings.openai import OpenAIEmbedding
        from llama_index.vector_stores.chroma import ChromaVectorStore
        from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
        import chromadb
    except ImportError as e:
        logger.warning("get_retrieval_context: import error %s", e)
        return ""

    try:
        inst = GitHubInstallation.objects.filter(installation_id=installation_id).first()
        if not inst or not inst.chroma_collection_name:
            return ""
    except Exception as e:
        logger.warning("get_retrieval_context: installation lookup failed %s", e)
        return ""

    persist_dir = getattr(settings, "CHROMA_PERSIST_DIR", None) or str(
        Path(settings.BASE_DIR) / "chroma_data"
    )
    try:
        client = chromadb.PersistentClient(path=persist_dir)
        collection = client.get_collection(name=inst.chroma_collection_name)
    except Exception as e:
        logger.warning("get_retrieval_context: chroma load failed %s", e)
        return ""

    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
        storage_context=storage_context,
    )

    if buckets:
        if len(buckets) == 1:
            filters = MetadataFilters(
                filters=[MetadataFilter(key="bucket", value=buckets[0], operator=FilterOperator.EQ)]
            )
        else:
            filters = MetadataFilters(
                filters=[MetadataFilter(key="bucket", value=buckets, operator=FilterOperator.IN)]
            )
        retriever = index.as_retriever(similarity_top_k=top_k, filters=filters)
        nodes = retriever.retrieve(query)
        source_nodes = nodes
    else:
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(query)
        source_nodes = getattr(response, "source_nodes", None) or []

    if not source_nodes:
        return ""

    max_chars = max_tokens * CHARS_PER_TOKEN
    parts = []
    total_chars = 0
    for node in source_nodes:
        text = node.node.text if hasattr(node, "node") else getattr(node, "text", str(node))
        meta = node.node.metadata if hasattr(node, "node") else getattr(node, "metadata", {}) or {}
        file_path = meta.get("file_path") or meta.get("file_name") or "document"
        block = f"File: {file_path}\n\nContent:\n{text}"
        if total_chars + len(block) > max_chars:
            remaining = max_chars - total_chars
            if remaining > 200:
                block = f"File: {file_path}\n\nContent:\n{text[:remaining]}..."
            else:
                break
        parts.append(block)
        total_chars += len(block)
        if total_chars >= max_chars:
            break

    if not parts:
        return ""
    return "\n\n---\n\n".join(parts)
