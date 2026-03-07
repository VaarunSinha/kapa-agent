"""
Mock agent: generate repository understanding markdown from tree text.
Deterministic; no LLM calls.
"""


def default_understanding(owner: str = "", repo_name: str = "") -> str:
    """Return mock understanding when no clone has run yet (so the field is never empty)."""
    repo_label = f"{owner}/{repo_name}".strip("/") or "this repository"
    return f"""# Repository understanding (mock)

Generated for **{repo_label}** before the first clone. You can edit this or re-run setup (Connect Source Code from Coverage Gaps) to regenerate from the repo tree.

## Repository structure

- Root: `{repo_name or "repo"}/`
- Documentation is typically under `docs/`.
- Look for `README.md`, `docs/api/`, and `docs/architecture/` for coverage.

## Documentation folders

- `docs/` – main documentation
- `docs/api/` – API reference (if present)
- `docs/architecture/` – architecture and design (if present)

## Potential documentation coverage areas

- Getting started and installation.
- API reference for public endpoints.
- Architecture and high-level design.
- Troubleshooting and FAQ.
"""


def generate_understanding(tree_text: str) -> str:
    """
    Given output of `git ls-files | tree --fromfile` (or similar), return
    understanding_of_project.md content: repository structure, documentation
    folders, potential doc coverage areas.
    """
    lines = (tree_text or "").strip().split("\n")
    doc_paths = [p for p in lines if "docs" in p.lower() or p.endswith(".md")]
    other_paths = [p for p in lines if p not in doc_paths][:30]
    return f"""# Repository understanding (generated)

## Repository structure

```
{chr(10).join(lines[:80])}
```

## Documentation folders

- Primary docs: `docs/` and markdown files throughout.
- Files identified: {len(doc_paths)} doc-related paths.

## Potential documentation coverage areas

- API documentation (see `docs/api/` if present).
- Architecture and overview (see `docs/architecture/` if present).
- Getting started and tutorials (see `docs/` root and tutorial paths).
- Ensure all public APIs and common user flows have corresponding docs.
"""
