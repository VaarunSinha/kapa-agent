"""
Research agent: query builder, vector retrieval, structured reasoner.
Returns either ask_questions (SurveyJS-compatible) or conclude_research (summary + files_referenced + coverage_gap_description).
Returns action "error" when LLM is unavailable or response is invalid.
"""
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

ERROR_LLM_UNAVAILABLE = "LLM unavailable"

# SurveyJS-compatible shape: question_text, question_type in ("text", "textarea", "choice"), choices (list of strings for choice)
# Note: OpenAI response_format requires "required" to include every key in "properties".

RESEARCH_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["ask_questions", "conclude_research"],
            "description": "Either ask clarifying questions or conclude with research summary",
        },
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question_text": {"type": "string"},
                    "question_type": {"type": "string", "enum": ["text", "textarea", "choice"]},
                    "choices": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["question_text", "question_type", "choices"],
                "additionalProperties": False,
            },
            "description": "Required when action is ask_questions",
        },
        "research_summary": {"type": "string"},
        "files_referenced": {"type": "array", "items": {"type": "string"}},
        "coverage_gap_description": {"type": "string"},
        "recommended_changes": {"type": "string"},
        "file_to_edit": {
            "type": "string",
            "description": "When action is conclude_research: the single documentation file path the writer should edit (must be from files_referenced). Empty when ask_questions.",
        },
        "confidence_score": {
            "type": "number",
            "description": "Confidence that the suggested documentation change addresses the gap (0-1). Required when action is conclude_research.",
            "minimum": 0,
            "maximum": 1,
        },
    },
    "required": [
        "action",
        "questions",
        "research_summary",
        "files_referenced",
        "file_to_edit",
        "coverage_gap_description",
        "recommended_changes",
        "confidence_score",
    ],
    "additionalProperties": False,
}

# Phase 1 (code-only) response schema
CODE_RESEARCH_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["ask_questions", "code_analyzed"],
            "description": "Either ask questions if code is insufficient, or code_analyzed with analysis",
        },
        "code_files": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Repo-relative paths of relevant code files",
        },
        "how_summary": {
            "type": "string",
            "description": "How the feature/behavior works (cause, mechanism, derivation) from the code",
        },
        "concepts_to_document": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key concepts/APIs to document",
        },
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question_text": {"type": "string"},
                    "question_type": {"type": "string", "enum": ["text", "textarea", "choice"]},
                    "choices": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["question_text", "question_type", "choices"],
                "additionalProperties": False,
            },
            "description": "Required when action is ask_questions",
        },
    },
    "required": ["action", "code_files", "how_summary", "concepts_to_document", "questions"],
    "additionalProperties": False,
}

# Phase 2 (doc placement) response schema — no action, always concludes
DOC_PLACEMENT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "research_summary": {"type": "string"},
        "files_referenced": {"type": "array", "items": {"type": "string"}},
        "file_to_edit": {
            "type": "string",
            "description": "The single documentation file path to edit (e.g. docs/architecture/agents.md). Must be one of the documentation paths where the change should be made.",
        },
        "coverage_gap_description": {"type": "string"},
        "recommended_changes": {"type": "string"},
        "confidence_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
    },
    "required": [
        "research_summary",
        "files_referenced",
        "file_to_edit",
        "coverage_gap_description",
        "recommended_changes",
        "confidence_score",
    ],
    "additionalProperties": False,
}

# Context budget (chars) so code is never truncated by doc
MAX_DOC_CHARS = 3500
MAX_BACKEND_CHARS = 2500
MAX_FRONTEND_CHARS = 2500


def _cap_context(s: str, max_chars: int) -> str:
    """Cap a context string to max_chars; append ... if truncated."""
    if not s or max_chars <= 0:
        return s or ""
    return s[:max_chars] + ("..." if len(s) > max_chars else "")


def _build_research_query(issue_title: str, issue_description: str, research_goal: str) -> str:
    """Build a single query for vector retrieval from issue fields."""
    parts = [issue_title or "", issue_description or "", research_goal or ""]
    return " ".join(p for p in parts if p).strip() or "Documentation structure and gaps"


def _build_code_query(issue_title: str, issue_description: str, research_goal: str) -> str:
    """Query tuned for matching implementation code (how it works, implementation)."""
    base = " ".join(
        p for p in [issue_title or "", issue_description or "", research_goal or ""] if p
    ).strip()
    if not base:
        return "implementation source code how it works"
    return f"{base} implementation source code how it works"


def _normalize_questions(out: dict) -> dict:
    """Extract and normalize questions from a response; return dict with action and questions."""
    valid_types = ("text", "textarea", "choice")
    questions = []
    for q in out.get("questions") or []:
        text = (q.get("question_text") or "").strip()
        if not text:
            continue
        qtype = (q.get("question_type") or "text").strip().lower()
        if qtype not in valid_types:
            qtype = "text"
        choices = q.get("choices")
        if not isinstance(choices, list):
            choices = [] if qtype == "choice" else None
        else:
            choices = [str(c).strip() for c in choices if c is not None]
        questions.append({
            "question_text": text,
            "question_type": qtype,
            "choices": choices if qtype == "choice" else (choices or None),
        })
    return {"action": "ask_questions", "questions": questions}


def _run_code_research(
    installation_id: int,
    issue_title: str,
    issue_description: str,
    research_goal: str,
    query: str,
    code_query: str,
) -> tuple:
    """
    Retrieve backend + frontend only; run code-analysis prompt.
    Returns (phase1_result_dict, backend_ctx, frontend_ctx).
    phase1_result_dict: {"action": "code_analyzed", "code_files", "how_summary", "concepts_to_document"}
    or {"action": "ask_questions", "questions": [...]} or {"action": "error", "error": "..."}.
    """
    from agent.retrieval import get_retrieval_context

    backend_ctx = get_retrieval_context(
        installation_id, code_query, top_k=8, max_tokens=650, buckets=["backend"]
    )
    frontend_ctx = get_retrieval_context(
        installation_id, code_query, top_k=8, max_tokens=650, buckets=["frontend"]
    )
    backend_ctx = _cap_context(backend_ctx, MAX_BACKEND_CHARS)
    frontend_ctx = _cap_context(frontend_ctx, MAX_FRONTEND_CHARS)
    code_context = ""
    if backend_ctx:
        code_context += "Backend excerpts:\n" + backend_ctx + "\n\n"
    if frontend_ctx:
        code_context += "Frontend excerpts:\n" + frontend_ctx
    if not code_context.strip():
        return (
            {
                "action": "ask_questions",
                "questions": [
                    {
                        "question_text": "No backend/frontend code was found for this repo. Is the repo indexed and does it contain implementation code for this topic?",
                        "question_type": "text",
                        "choices": [],
                    }
                ],
            },
            backend_ctx,
            frontend_ctx,
        )

    from agent.agents.openai_structured import structured_completion
    from agent.prompts import CODE_RESEARCH_SYSTEM, CODE_RESEARCH_USER_TEMPLATE

    user_prompt = CODE_RESEARCH_USER_TEMPLATE.format(
        issue_title=issue_title or "N/A",
        issue_description=issue_description or "N/A",
        research_goal=research_goal or "N/A",
        code_context=code_context,
    )
    out = structured_completion(
        system_prompt=CODE_RESEARCH_SYSTEM,
        user_prompt=user_prompt,
        json_schema=CODE_RESEARCH_RESPONSE_SCHEMA,
        model="gpt-4o",
    )
    if out is None:
        return ({"action": "error", "error": ERROR_LLM_UNAVAILABLE}, backend_ctx, frontend_ctx)
    if out.get("action") == "ask_questions" and out.get("questions"):
        return (_normalize_questions(out), backend_ctx, frontend_ctx)
    return (
        {
            "action": "code_analyzed",
            "code_files": out.get("code_files") or [],
            "how_summary": out.get("how_summary") or "",
            "concepts_to_document": out.get("concepts_to_document") or [],
        },
        backend_ctx,
        frontend_ctx,
    )


def _run_doc_placement(
    issue_title: str,
    issue_description: str,
    research_goal: str,
    code_files: list,
    how_summary: str,
    concepts_to_document: list,
    installation_id: int,
    query: str,
    user_answers_section: str,
) -> dict:
    """
    Retrieve documentation only; run doc-placement prompt.
    Returns same shape as current conclude_research: research_summary, files_referenced,
    coverage_gap_description, recommended_changes, confidence_score.
    """
    from agent.retrieval import get_retrieval_context

    doc_ctx = get_retrieval_context(
        installation_id, query, top_k=10, max_tokens=900, buckets=["documentation"]
    )
    doc_ctx = _cap_context(doc_ctx, MAX_DOC_CHARS)
    if not doc_ctx.strip():
        doc_ctx = "(No documentation excerpts retrieved.)"

    from agent.agents.openai_structured import structured_completion
    from agent.prompts import DOC_PLACEMENT_SYSTEM, DOC_PLACEMENT_USER_TEMPLATE

    user_prompt = DOC_PLACEMENT_USER_TEMPLATE.format(
        issue_title=issue_title or "N/A",
        issue_description=issue_description or "N/A",
        research_goal=research_goal or "N/A",
        how_summary=how_summary or "—",
        concepts_to_document="\n".join(concepts_to_document) if concepts_to_document else "—",
        code_files="\n".join(code_files) if code_files else "—",
        documentation_context=doc_ctx,
        user_answers_section=user_answers_section,
    )
    out = structured_completion(
        system_prompt=DOC_PLACEMENT_SYSTEM,
        user_prompt=user_prompt,
        json_schema=DOC_PLACEMENT_RESPONSE_SCHEMA,
        model="gpt-4o",
    )
    if out is None:
        return {
            "action": "error",
            "error": ERROR_LLM_UNAVAILABLE,
        }
    # Merge code_files into files_referenced (doc placement may add doc paths)
    doc_files = [f for f in (out.get("files_referenced") or []) if f and f not in code_files]
    files_referenced = list(code_files) + doc_files

    raw_confidence = out.get("confidence_score")
    try:
        confidence = float(raw_confidence) if raw_confidence is not None else None
        if confidence is not None and (confidence < 0 or confidence > 1):
            confidence = None
    except (TypeError, ValueError):
        confidence = None
    return {
        "action": "research",
        "summary": out.get("research_summary") or "",
        "files_referenced": files_referenced,
        "file_to_edit": out.get("file_to_edit") or "",
        "coverage_gap_description": out.get("coverage_gap_description") or "",
        "recommended_changes": out.get("recommended_changes") or "",
        "confidence_score": confidence,
    }


def _run_researcher_fallback(
    issue_title: str,
    issue_description: str,
    research_goal: str,
    retrieval_context: str,
    user_answers_section: str,
) -> dict:
    """Single-prompt fallback when installation_id is not set (e.g. no indexed repo)."""
    from agent.agents.openai_structured import structured_completion
    from agent.prompts import RESEARCHER_SYSTEM, RESEARCHER_USER_TEMPLATE

    user_prompt = RESEARCHER_USER_TEMPLATE.format(
        issue_title=issue_title or "N/A",
        issue_description=issue_description or "N/A",
        research_goal=research_goal or "N/A",
        retrieval_context=retrieval_context or "(No retrieval context available.)",
        user_answers_section=user_answers_section,
    )
    out = structured_completion(
        system_prompt=RESEARCHER_SYSTEM,
        user_prompt=user_prompt,
        json_schema=RESEARCH_RESPONSE_SCHEMA,
        model="gpt-4o",
    )
    if out is None:
        return {"action": "error", "error": ERROR_LLM_UNAVAILABLE}
    if out.get("action") == "ask_questions" and out.get("questions"):
        questions = _normalize_questions(out)
        if questions.get("questions"):
            return questions
    if out.get("action") == "conclude_research":
        raw_confidence = out.get("confidence_score")
        try:
            confidence = float(raw_confidence) if raw_confidence is not None else None
            if confidence is not None and (confidence < 0 or confidence > 1):
                confidence = None
        except (TypeError, ValueError):
            confidence = None
        return {
            "action": "research",
            "summary": out.get("research_summary") or "Research completed.",
            "files_referenced": out.get("files_referenced") or [],
            "file_to_edit": out.get("file_to_edit") or "",
            "coverage_gap_description": out.get("coverage_gap_description") or "",
            "recommended_changes": out.get("recommended_changes") or "",
            "confidence_score": confidence,
        }
    return {"action": "error", "error": "invalid response shape"}


def run_researcher(
    issue_title: str,
    issue_description: str,
    repository_tree: str,
    retrieval_context: str = "",
    installation_id: Optional[int] = None,
    research_goal: str = "",
    user_answers: str = "",
) -> dict:
    """
    Returns either:
    - {"action": "questions", "questions": [{"question_text", "question_type", "choices"?}, ...]}
    - {"action": "research", "summary": str, "files_referenced": [...], "coverage_gap_description": str, ...}
    - {"action": "error", "error": "..."}
    When installation_id is set: runs code-first (phase 1) then doc-placement (phase 2). Otherwise uses single-prompt fallback.
    """
    query = _build_research_query(issue_title, issue_description, research_goal)
    if not query and issue_title:
        query = issue_title
    code_query = _build_code_query(issue_title, issue_description, research_goal)

    user_answers_section = ""
    if (user_answers or "").strip():
        user_answers_section = (
            "\n\nUser provided the following answers:\n"
            + (user_answers or "").strip()
            + "\n\nUse these to conclude research. You MUST respond with action: conclude_research."
        )

    if installation_id:
        phase1, _, _ = _run_code_research(
            installation_id,
            issue_title,
            issue_description,
            research_goal,
            query,
            code_query,
        )
        if phase1.get("action") == "ask_questions":
            return phase1
        if phase1.get("action") == "error":
            return phase1
        # phase1["action"] == "code_analyzed"
        return _run_doc_placement(
            issue_title=issue_title,
            issue_description=issue_description,
            research_goal=research_goal,
            code_files=phase1.get("code_files") or [],
            how_summary=phase1.get("how_summary") or "",
            concepts_to_document=phase1.get("concepts_to_document") or [],
            installation_id=installation_id,
            query=query,
            user_answers_section=user_answers_section,
        )

    # No installation_id: single-prompt fallback
    return _run_researcher_fallback(
        issue_title=issue_title,
        issue_description=issue_description,
        research_goal=research_goal,
        retrieval_context=retrieval_context,
        user_answers_section=user_answers_section,
    )
