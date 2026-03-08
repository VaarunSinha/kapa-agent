"""
Style extraction agent: infer documentation voice from 3–5 representative docs.
Output schema → style.md for Writer and Fix Assistant.
"""
from agent.agents.openai_structured import structured_completion
from agent.prompts import STYLE_SYSTEM, STYLE_USER_TEMPLATE

STYLE_SCHEMA = {
    "type": "object",
    "properties": {
        "tone": {"type": "string", "description": "Overall tone (e.g. professional, friendly)"},
        "sentence_style": {"type": "string", "description": "Sentence structure preferences"},
        "structure_rules": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Rules for doc structure",
        },
        "formatting_rules": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Formatting conventions",
        },
        "example_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "How examples are presented",
        },
    },
    "required": [
        "tone",
        "sentence_style",
        "structure_rules",
        "formatting_rules",
        "example_patterns",
    ],
    "additionalProperties": False,
}


def extract_style(sample_docs_content: str) -> str:
    """
    Infer documentation style from sample doc content. Returns Markdown (style.md).
    If OpenAI is not configured or call fails, returns a minimal default style.
    """
    if not (sample_docs_content or "").strip():
        return _default_style_md()

    user_prompt = STYLE_USER_TEMPLATE.format(
        sample_docs_content=sample_docs_content[:12000],
    )
    out = structured_completion(
        system_prompt=STYLE_SYSTEM,
        user_prompt=user_prompt,
        json_schema=STYLE_SCHEMA,
        model="gpt-4o",
    )
    if not out:
        return _default_style_md()

    lines = [
        "# Documentation style",
        "",
        "## Tone",
        out.get("tone", ""),
        "",
        "## Sentence style",
        out.get("sentence_style", ""),
        "",
        "## Structure rules",
    ]
    for r in out.get("structure_rules") or []:
        lines.append(f"- {r}")
    lines.extend(["", "## Formatting rules"])
    for r in out.get("formatting_rules") or []:
        lines.append(f"- {r}")
    lines.extend(["", "## Example patterns"])
    for p in out.get("example_patterns") or []:
        lines.append(f"- {p}")
    return "\n".join(lines)


def _default_style_md() -> str:
    return """# Documentation style

## Tone
Professional and clear.

## Sentence style
Use complete sentences; prefer active voice.

## Structure rules
- Use headings to organize content.
- Put overview first, then details.

## Formatting rules
- Use markdown for code blocks and lists.
- Keep line length readable.

## Example patterns
- Prefer concise, runnable examples where applicable.
"""