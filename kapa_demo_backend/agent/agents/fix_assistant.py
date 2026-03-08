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
    files_blob = "\n\n---FILE---\n\n".join(
        f"Path: {f.get('path', '')}\nContent:\n{f.get('content', '')}"
        for f in files
    )[:12000]
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
