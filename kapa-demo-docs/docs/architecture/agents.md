---
sidebar_position: 2
title: Agents
---

# Agents

The pipeline uses four agents: **Issue Creator**, **Research Agent**, **Writer Agent**, and **Fix Assistant**. Each has a narrow role; the backend orchestrates them and owns all GitHub and repository I/O.

## Issue Creator

The Issue Creator turns a coverage gap into a structured issue for the rest of the pipeline. Given the gap title, finding, suggestion, and repository understanding, it produces:

- **Title** — Short issue title suitable for GitHub
- **Description** — Body text for the issue
- **Research goal** — Focus for the Research Agent

The backend creates an `Issue` record with these fields and enqueues the research task.

## Research Agent

The Research Agent answers: *What in this repository is relevant to this documentation gap?*

It receives the issue (title, description, research goal) and repository context. The system gathers relevant documentation and code content and passes it to the agent. The agent analyzes that content, extracts implementation details, and summarizes how the feature or API works. The result is a **research report**: a structured document that references specific files and code sections and highlights findings that should be reflected in the documentation.

The research report is the main input for the Writer Agent. It can also emit **questions** (e.g., choice or free text) when it needs clarification; the backend stores these and re-runs research after answers are submitted.

### Output format

The research report typically includes:

- **Relevant files** — Paths and short descriptions of why each file matters
- **Code excerpts** — Important snippets (signatures, config, key logic)
- **Findings** — Bullet or narrative summary of behavior, edge cases, or caveats
- **Coverage gap description** — Summary tailored to the documentation gap
- **Open questions** — When the agent chooses to ask instead of conclude, the list of questions for the user

The exact schema is defined in the backend and consumed by the Writer Agent.

## Writer Agent

The Writer Agent turns the research report into documentation. It is given:

- The research report
- Existing documentation content when updating specific files
- A **style guide** so that generated docs match the project’s writing style

It produces:

- **New or updated doc files** — Markdown (or other formats) ready to be committed
- **Open questions for engineers** — Optional list for the PR description or a comment

The Writer does not call the repository or GitHub directly; it only works with the content provided in the research report and any existing doc content and style guidance the backend supplies. The backend is responsible for writing the agent’s output to the correct paths and creating the pull request.

### Style alignment

The system aligns documentation with the project’s writing style. A style guide is used by the Writer Agent (and by the Fix Assistant when applying edits). This keeps tone, structure, and formatting consistent across generated and edited docs.

## Fix Assistant

The Fix Assistant supports editing a proposed fix from the UI. When the user requests changes (e.g., “add a code example here” or “shorten this section”), the assistant applies those edits to the fix content. The backend then updates the Fix record; if the fix is already published, it can push an additional commit to the same branch. The Fix Assistant uses the same style guide as the Writer so that edits remain consistent with the rest of the docs.

## Pipeline summary

1. **Coverage gap** — User clicks Act; Issue Creator produces issue fields; backend creates Issue and enqueues research.
2. **Research** — Relevant content is gathered; the Research Agent analyzes it and either asks questions or produces a research report.
3. **Questions** — If questions were asked, user submits answers; research is re-run and eventually concludes with a report.
4. **Writing** — Writer Agent uses the report and style guide to draft documentation files.
5. **Fix** — Backend creates a Fix with the proposed files; user can review and edit via the Fix Assistant, then approve.
6. **Publish** — Backend creates a branch, commits the fix, opens a PR, and can comment on the issue.

No agent talks to GitHub or the version control system directly; the backend owns all external I/O and orchestration.
