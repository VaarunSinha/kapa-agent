"""Shared utilities for the agent app."""
import difflib


def unified_diff_string(old_content: str, new_content: str, path: str = "") -> str:
    """
    Produce a unified diff string between old and new content.
    Empty old_content is treated as a new file (all additions).
    """
    a = (old_content or "").splitlines()
    b = (new_content or "").splitlines()
    path = path or "file"
    lines = list(
        difflib.unified_diff(
            a,
            b,
            fromfile=path,
            tofile=path,
            lineterm="",
        )
    )
    return "\n".join(lines) if lines else ""
