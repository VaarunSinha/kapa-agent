"""
Mock writer agent: given research summary, returns list of fix payloads (multi-file).
Deterministic; no LLM calls. If real file_path and file_content are provided, edits one line for a visible diff.
"""


def _edit_one_line(content: str, issue_title: str) -> str:
    """Apply a single deterministic edit so the diff view shows one clear change."""
    title = (issue_title or "Documentation update")[:80]
    line = f"\n\n<!-- Documentation updated for: {title} -->\n"
    return (content.rstrip() if content else "") + line


def run_writer(
    research_summary: str,
    issue_title: str = "",
    file_path: str = None,
    file_content: str = None,
) -> list:
    """
    Returns list of fixes, each: {"summary": str, "files": [{"path": str, "content": str}, ...]}
    If file_path and file_content are provided, returns one fix with that file edited by one line (visible diff).
    """
    title = issue_title or "Documentation update"
    if file_path and file_content is not None:
        edited = _edit_one_line(file_content, title)
        return [
            {
                "summary": f"Docs update for: {title}",
                "files": [{"path": file_path, "content": edited}],
            }
        ]
    return [
        {
            "summary": f"Docs update for: {title}",
            "files": [
                {
                    "path": "docs/getting-started.md",
                    "content": "# Getting Started\n\n## Installation\n\n1. Install the CLI:\n   ```bash\n   npm install -g @kapa/cli\n   ```\n2. Log in:\n   ```bash\n   kapa login\n   ```\n"
                    + _edit_one_line("", title).strip(),
                },
                {
                    "path": "docs/README.md",
                    "content": "# Documentation\n\nThis documentation covers setup and usage.\n\n"
                    + (research_summary[:200] if research_summary else "")
                    + _edit_one_line("", title).strip(),
                },
            ],
        }
    ]
