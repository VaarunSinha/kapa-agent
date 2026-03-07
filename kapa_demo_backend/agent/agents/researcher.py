"""
Mock researcher agent: given Issue + repo tree, returns either questions (SurveyJS-compatible)
or research summary. Deterministic; no LLM calls. Uses real tree to build path-based questions.
"""
import re

# SurveyJS-compatible shape: question_text, question_type in ("text", "textarea", "choice"), choices (list of strings for choice)


def _doc_paths_from_tree(repository_tree: str):
    """Extract doc-like paths (.md or under docs/) from raw tree or markdown code block."""
    if not (repository_tree or "").strip():
        return []
    raw = (repository_tree or "").strip()
    code_block = re.search(r"```\s*\n(.*?)```", raw, re.DOTALL)
    if code_block:
        raw = code_block.group(1)
    paths = []
    for line in raw.splitlines():
        path = line.strip().strip("/").split("\t")[0].strip()
        if not path or path.startswith("#"):
            continue
        if path.endswith(".md") or "docs" in path.lower():
            paths.append(path)
    return paths[:20]


def run_researcher(issue_title: str, issue_description: str, repository_tree: str) -> dict:
    """
    Returns either:
    - {"action": "questions", "questions": [{"question_text": str, "question_type": "text"|"textarea"|"choice", "choices": [...]?}, ...]}
    - {"action": "research", "summary": str}
    """
    doc_paths = _doc_paths_from_tree(repository_tree or "")
    path_choices = doc_paths[:8] if doc_paths else ["docs/README.md", "docs/getting-started.md"]
    title_lower = (issue_title or "").lower()
    if "authentication" in title_lower or doc_paths:
        questions = []
        if doc_paths:
            questions.append({
                "question_text": "Which file should we update for this gap?",
                "question_type": "choice",
                "choices": path_choices,
            })
        questions.extend([
            {
                "question_text": "How often do users run into this gap in practice?",
                "question_type": "choice",
                "choices": ["Rarely", "Sometimes", "Often", "Very often"],
            },
            {
                "question_text": "Should we add a code example here?",
                "question_type": "choice",
                "choices": ["Yes", "No", "Only if simple"],
            },
            {
                "question_text": "Any other context we should include?",
                "question_type": "textarea",
            },
        ])
        return {"action": "questions", "questions": questions}
    return {
        "action": "research",
        "summary": (
            "Analyzed repository and issue. The gap appears when users ask about this topic; "
            "current docs could be extended. Recommend adding a short section with clear steps and examples."
            + (f" Candidate paths: {', '.join(doc_paths[:5])}." if doc_paths else "")
        ),
    }
