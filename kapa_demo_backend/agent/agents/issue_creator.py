"""
Issue Creator agent: CoverageGap + project understanding → title, description, research_goal.
Structured output when OPENAI_API_KEY is set; else deterministic fallback.
"""
from typing import Any, Optional

from agent.agents.openai_structured import structured_completion
from agent.prompts import ISSUE_CREATOR_SYSTEM, ISSUE_CREATOR_USER_TEMPLATE

ISSUE_CREATOR_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Issue title"},
        "description": {"type": "string", "description": "Issue description"},
        "research_goal": {"type": "string", "description": "Goal for the research phase"},
    },
    "required": ["title", "description", "research_goal"],
    "additionalProperties": False,
}


def create_issue_from_gap(
    gap_title: str,
    gap_finding: str,
    gap_suggestion: str,
    understanding: str,
) -> dict[str, Any]:
    """
    Return { title, description, research_goal } for the issue.
    Uses LLM when available; otherwise returns sensible defaults from gap fields.
    """
    understanding_excerpt = (understanding or "")[:4000]
    user_prompt = ISSUE_CREATOR_USER_TEMPLATE.format(
        gap_title=gap_title,
        gap_finding=gap_finding,
        gap_suggestion=gap_suggestion,
        understanding_excerpt=understanding_excerpt,
    )
    out: Optional[dict] = structured_completion(
        system_prompt=ISSUE_CREATOR_SYSTEM,
        user_prompt=user_prompt,
        json_schema=ISSUE_CREATOR_SCHEMA,
        model="gpt-4o",
    )
    if out:
        return {
            "title": (out.get("title") or gap_title)[:255],
            "description": out.get("description") or gap_finding or "",
            "research_goal": out.get("research_goal") or gap_suggestion or "",
        }
    return {
        "title": (gap_title or "Documentation gap")[:255],
        "description": gap_finding or "",
        "research_goal": gap_suggestion or "",
    }
