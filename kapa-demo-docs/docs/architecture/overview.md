---
sidebar_position: 1
title: Architecture Overview
---

# Architecture Overview

The Kapa Content Gap Action Agent is built as a Next.js frontend, a Django backend with Celery, a GitHub App integration, vector retrieval (LlamaIndex), and several AI agents. GitHub is used for issues and for output (comments, pull requests).

## High-level flow

1. **Coverage gap** — Identified from conversations or analytics; stored with title, finding, suggestion.
2. **Issue** — User acts on a gap; backend creates an Issue (Issue Creator agent) and enqueues work.
3. **Research** — Celery runs the Research Agent with repository and documentation context. It may ask questions or produce a research report.
4. **Questions** — If the agent asks questions, the frontend collects answers; backend re-runs research with answers.
5. **Fix** — Writer Agent produces documentation changes from the research report. Fixes may affect multiple files. A Fix record holds the proposed changes.
6. **Review** — User reviews the fix in the UI; edits can be made via the Fix Assistant. Approval triggers publish.
7. **Pull request** — Backend creates a branch, commits the fix, and opens a PR; optionally comments on the issue.

Documentation fixes may affect multiple files; the system supports proposing and reviewing such changes in one fix.

## Components

### Frontend

A **Next.js** application (`kapa-demo`) that provides:

- Dashboard with coverage gaps and metrics
- List and detail views for issues, research, and fixes
- Fix preview and Fix Assistant for editing proposed docs
- Integration with the Django backend over HTTP (no direct GitHub or agent calls)

### Backend

A **Django** service (`kapa_demo_backend`) that:

- Exposes REST endpoints for coverage gaps, issues, research, questions, and fixes
- Runs Celery tasks: create_issue_task, research_issue_task, publish_fixes_task
- Uses the GitHub App for repo access, branches, commits, and PRs
- Stores CoverageGap, Issue, Research, Question, Fix and related state

### Vector retrieval

The backend uses **LlamaIndex** with a vector store to provide relevant documentation and code context to the Research and Writer agents. Indexing is tied to the connected GitHub installation.

### Agents

- **Issue Creator**: Turns a coverage gap (title, finding, suggestion) into an issue title, description, and research goal using repo understanding.
- **Research Agent**: Consumes issue context and relevant content, produces a research report or asks questions.
- **Writer Agent**: Consumes the research report and style guidance, produces documentation file content.
- **Fix Assistant**: Applies user edits from the UI to fix content (used during review).

See [Agents](/docs/architecture/agents) for more detail.

### GitHub integration

The backend uses a **GitHub App** to read repository content, create branches and commits, open pull requests, and comment on issues. See [GitHub integration](/docs/api/github-integration).

## Data flow

```
Coverage Gap → Act → Issue → Research (→ Questions → Research) → Fix → Approve → PR
```

The frontend drives the flow by calling the backend API; Celery runs research and publish tasks. The backend is the single point of integration with GitHub and the only component that runs the agents.
