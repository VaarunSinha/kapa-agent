---
sidebar_position: 2
title: Agents
---

# Agents

The pipeline is driven by two agents: a **research agent** that analyzes the repository and a **writer agent** that drafts documentation from the research output.

## Research Agent

The research agent answers the question: *What in this repository is relevant to this documentation gap?*

It receives the documentation question (e.g., from a GitHub issue title and body) and the target repository context. The system selects relevant files from the repository and passes them to the agent for analysis. The agent inspects those files, extracts implementation details, and summarizes how the feature or API works. The result is a **research report**: a structured document that references specific files and code sections and highlights findings that should be reflected in the documentation.

The research report is the single source of truth for the writer. It avoids having the writer agent re-scan the entire repo and keeps the documentation draft aligned with the actual code paths and behavior identified during research.

### Output format

The research report typically includes:

- **Relevant files**: Paths and short descriptions of why each file matters
- **Code excerpts**: Important snippets (signatures, config, key logic)
- **Findings**: Bullet or narrative summary of behavior, edge cases, or caveats
- **Open questions**: Anything the research could not resolve (e.g., unclear defaults, multiple implementations) that engineers might need to clarify

The exact schema is defined in the backend and consumed by the writer agent.

## Writer Agent

The writer agent turns the research report into documentation. It is given:

- The research report
- The target documentation format and structure (e.g., Docusaurus Markdown, section hierarchy)
- Optional style or template guidelines

It produces:

- **New or updated doc files**: Markdown (or other formats) ready to be committed
- **Open questions for engineers**: A list that can be added to the PR description or a comment so reviewers can confirm or correct assumptions

The writer does not call the repository or GitHub directly; it only works with the content provided in the research report and any existing doc content the backend supplies.

### Integration with the repo

The backend is responsible for:

- Checking out or fetching the target branch
- Providing existing documentation files to the writer when updating (e.g., for “update this page” tasks)
- Writing the agent’s output to the correct paths and creating the pull request

The writer agent’s output is therefore file-oriented: paths and body content. The backend handles branch naming, commit messages, and PR creation.

## Pipeline summary

1. **Input**: Documentation gap (issue or task) + repository identifier.
2. **Research**: Relevant files are selected; the research agent analyzes them and produces a research report.
3. **Writing**: The writer agent uses the report to draft documentation and optional open questions.
4. **Output**: The backend creates a branch, commits the changes, opens a PR, and can comment on the original issue.

No agent talks to GitHub or the version control system directly; the backend owns all external I/O and orchestration.
