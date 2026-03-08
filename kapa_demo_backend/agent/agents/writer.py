"""
Writer agent: research + retrieval context + style.md → structured output files[] (edit existing docs).
Uses LLM only; returns [] when LLM unavailable or returns no files.
"""
import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

WRITER_SCHEMA = {
    "type": "object",
    "properties": {
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {
                        "type": "string",
                        "description": "Full file content = existing content with only the requested additions or edits; do not omit or rewrite existing sections.",
                    },
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
            "description": "Documentation files to create or update (path and full content)",
        },
    },
    "required": ["files"],
    "additionalProperties": False,
}


def run_writer(
    research_summary: str,
    issue_title: str = "",
    file_path: Optional[str] = None,
    file_content: Optional[str] = None,
    retrieval_context: str = "",
    style_md: str = "",
    files_referenced: Optional[List[str]] = None,
    coverage_gap_description: str = "",
    recommended_changes: str = "",
) -> list:
    """
    Returns list of fixes, each: {"summary": str, "files": [{"path": str, "content": str}, ...]}
    Uses LLM only; returns [] when LLM unavailable or returns no files.
    """
    title = issue_title or "Documentation update"

    from agent.agents.openai_structured import structured_completion
    from agent.prompts import WRITER_SYSTEM, WRITER_USER_TEMPLATE

    files_referenced_str = ", ".join(files_referenced or [])
    style_md_snippet = (style_md or "")[:3000]
    retrieval_snippet = (retrieval_context or "")[:5000]
    user_prompt = WRITER_USER_TEMPLATE.format(
        research_summary=research_summary or "N/A",
        coverage_gap_description=coverage_gap_description or "N/A",
        recommended_changes=recommended_changes or "N/A",
        title=title,
        files_referenced_str=files_referenced_str,
        style_md=style_md_snippet,
        retrieval_context=retrieval_snippet,
    )
    if file_path and file_content is not None:
        # Send the whole file (cap at 100k chars for context limits; prefer no truncation)
        file_snippet = (file_content or "")[:100000]
        user_prompt += (
            f"\n\nThe following is the complete file to edit (path: {file_path}):\n<content>\n{file_snippet}\n</content>\n\n"
            "Your response must be this entire content with only your additions inserted. Add only; do not delete, summarize, or replace any existing sections."
        )

    out = structured_completion(
        system_prompt=WRITER_SYSTEM,
        user_prompt=user_prompt,
        json_schema=WRITER_SCHEMA,
        model="gpt-4o-mini",
    )
    if out and out.get("files"):
        return [
            {
                "summary": f"Docs update for: {title}",
                "files": [{"path": f.get("path", ""), "content": f.get("content", "")} for f in out["files"]],
            }
        ]
    logger.warning(
        "run_writer: no files produced (LLM unavailable or empty response) issue_title=%s",
        title[:80],
    )
    return []
