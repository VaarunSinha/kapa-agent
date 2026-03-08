"""
Generate repository understanding markdown from tree text.
Uses structured LLM output when OPENAI_API_KEY is set; otherwise placeholder/fallback.
Produces a concise architecture map (frontend, backend, documentation, key directories).
"""

from agent.prompts import (
    UNDERSTANDING_SYSTEM,
    UNDERSTANDING_USER_TEMPLATE,
)

# JSON schema for structured project understanding (OpenAI response_format)
PROJECT_UNDERSTANDING_SCHEMA = {
    "type": "object",
    "properties": {
        "project_summary": {
            "type": "string",
            "description": "Short technical summary of the repository",
        },
        "frontend": {
            "type": "string",
            "description": "Description of the frontend application and its main location",
        },
        "backend": {
            "type": "string",
            "description": "Description of backend services and architecture",
        },
        "documentation": {
            "type": "string",
            "description": "Explanation of how documentation is organized",
        },
        "directories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "purpose": {"type": "string"},
                    "bucket": {
                        "type": "string",
                        "enum": ["documentation", "frontend", "backend", "other"],
                        "description": "Category for this directory",
                    },
                },
                "required": ["path", "purpose", "bucket"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "project_summary",
        "frontend",
        "backend",
        "documentation",
        "directories",
    ],
    "additionalProperties": False,
}

def default_understanding(owner: str = "", repo_name: str = "") -> str:
    """Return placeholder understanding when no clone has run yet (so the field is never empty)."""
    repo_label = f"{owner}/{repo_name}".strip("/") or "this repository"
    return f"""# Repository Understanding

Repository not yet analyzed. Connect source code and complete setup (Connect Source Code from Coverage Gaps) to generate understanding for **{repo_label}**.
"""


def generate_understanding(tree_text: str) -> str:
    """
    Given output of `git ls-files | tree --fromfile` (or similar), return
    understanding_of_project.md content without LLM: structure, docs, key dirs.
    Used as fallback when structured LLM call fails.
    """
    lines = (tree_text or "").strip().split("\n")
    doc_paths = [p for p in lines if "docs" in p.lower() or p.endswith(".md")]
    return f"""# Repository Understanding

## Project Summary

Repository structure inferred from file tree.

## Frontend

Infer from tree: look for directories such as `app/`, `src/`, or framework-specific names (e.g. Next.js, React).

## Backend

Infer from tree: look for server code, API routes, or backend service directories.

## Documentation

Primary docs: `docs/` and markdown files throughout. {len(doc_paths)} doc-related paths identified.

## Key Directories

- `docs/` — main documentation
- `docs/api/` — API reference (if present)
- `docs/architecture/` — architecture and overview (if present)
"""


def _render_understanding_markdown(out: dict) -> str:
    """Convert structured JSON to markdown per spec."""
    lines = [
        "# Repository Understanding",
        "",
        "## Project Summary",
        out.get("project_summary", ""),
        "",
        "## Frontend",
        out.get("frontend", ""),
        "",
        "## Backend",
        out.get("backend", ""),
        "",
        "## Documentation",
        out.get("documentation", ""),
        "",
        "## Key Directories",
    ]
    for d in out.get("directories") or []:
        path = d.get("path", "")
        purpose = d.get("purpose", "")
        bucket = d.get("bucket", "other")
        lines.append(f"- `{path}` — {purpose} ({bucket})")
    return "\n".join(lines)


def generate_understanding_structured(tree_text: str, sample_doc_preview: str = ""):
    """
    Generate understanding via LLM structured output; fall back to generate_understanding if no key or call fails.
    Returns (markdown_str, raw_dict). raw_dict is None on failure; callers can use it for path→bucket mapping.
    """
    import logging
    from agent.agents.openai_structured import structured_completion

    logger = logging.getLogger(__name__)
    tree_snippet = (tree_text or "").strip()[:8000]
    doc_snippet = (sample_doc_preview or "").strip()[:2000]

    user_prompt = UNDERSTANDING_USER_TEMPLATE.format(
        tree_text=tree_snippet,
        sample_doc_preview=doc_snippet,
    )

    out = structured_completion(
        system_prompt=UNDERSTANDING_SYSTEM,
        user_prompt=user_prompt,
        json_schema=PROJECT_UNDERSTANDING_SCHEMA,
        model="gpt-4o",
    )
    if not out:
        logger.warning(
            "generate_understanding_structured: LLM unavailable or failed, using tree-only fallback",
        )
        return (generate_understanding(tree_text), None)

    return (_render_understanding_markdown(out), out)
