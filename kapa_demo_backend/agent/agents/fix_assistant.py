"""
Fix Assistant: existing markdown + user instruction + style.md → updated markdown (gpt-4o-mini).
"""
from typing import Any, List, Optional

FIX_ASSISTANT_SCHEMA = {
    "type": "object",
    "properties": {
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
        },
        "assistant_message": {"type": "string"},
    },
    "required": ["files", "assistant_message"],
    "additionalProperties": False,
}


def apply_fix_instruction(
    files: List[dict],
    user_message: str,
    style_md: str = "",
) -> Optional[dict]:
    """
    Apply user instruction to fix files. Returns None on failure, or a dict:
    {"files": [{"path", "content"}, ...], "assistant_message": "brief description for user"}.
    """
    from agent.agents.openai_structured import structured_completion
    from agent.prompts import FIX_ASSISTANT_SYSTEM, FIX_ASSISTANT_USER_TEMPLATE

    if not user_message or not files:
        return None
    chunks = []
    for f in files:
        path = f.get("path") or f.get("file_path") or ""
        content = f.get("content") or f.get("diff") or f.get("patch") or ""
        original = f.get("original_content")
        parts = [f"Path: {path}"]
        if original is not None and original != "":
            parts.append("Original file (base to preserve):\n<original>\n" + original + "\n</original>")
        parts.append("Current draft:\n<current>\n" + content + "\n</current>")
        chunks.append("\n".join(parts))
    # Truncate at file boundary so we never cut mid-file (avoids partial content from LLM)
    max_blob_len = 16000
    sep = "\n\n---FILE---\n\n"
    if not chunks:
        files_blob = ""
    else:
        files_blob = chunks[0]
        if len(files_blob) > max_blob_len:
            files_blob = files_blob[:max_blob_len]
        else:
            for c in chunks[1:]:
                if len(files_blob) + len(sep) + len(c) <= max_blob_len:
                    files_blob = files_blob + sep + c
                else:
                    break
    style_block = f"\n\nStyle guide to follow:\n{style_md[:2000]}" if style_md else ""
    user_prompt = FIX_ASSISTANT_USER_TEMPLATE.format(
        files_blob=files_blob,
        style_block=style_block,
        user_message=user_message,
    )
    out = structured_completion(
        system_prompt=FIX_ASSISTANT_SYSTEM,
        user_prompt=user_prompt,
        json_schema=FIX_ASSISTANT_SCHEMA,
        model="gpt-4o-mini",
    )
    if not out or not out.get("files"):
        return None
    return {
        "files": out["files"],
        "assistant_message": (out.get("assistant_message") or "").strip(),
    }
