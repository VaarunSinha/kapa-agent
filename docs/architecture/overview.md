---
sidebar_position: 1
title: Architecture Overview
---

# Architecture Overview

The Kapa Content Gap Action Agent is built as a frontend, a backend orchestrator, and a set of agents that perform research and writing. GitHub is used for input (issues) and output (comments, pull requests).

## High-level flow

1. A documentation gap is reported via a GitHub issue.
2. The backend receives the trigger (from the frontend or from a webhook) and starts the research processor.
3. The research agent analyzes the repository and identifies relevant files. Findings are summarized into a research report.
4. The writer agent consumes the research report and drafts documentation changes.
5. The backend creates a pull request with the proposed documentation and any open questions for engineers.

## Components

### Frontend

A **Next.js** application that provides:

- A way to trigger documentation tasks (e.g., by linking a GitHub issue or entering a topic)
- Status views for running or completed tasks
- Links to generated pull requests

The frontend talks to the Django backend over HTTP. It does not call GitHub or run agents directly.

### Backend

A **Django** service that:

- Exposes REST endpoints for the frontend and (optionally) webhooks
- Orchestrates the research and writer agents
- Communicates with GitHub (read repo content, comment on issues, create branches and pull requests)
- Stores task state and research outputs as needed

### Research Agent

The research agent is responsible for understanding the codebase in the context of a documentation question. It receives the issue or topic, selects relevant files from the repository, and produces a structured research report that the writer agent uses as input. The report typically includes file references, code excerpts, and summarized findings.

### Writer Agent

The writer agent takes the research report and generates documentation content. It produces new or updated Markdown (or other doc formats) and can attach a list of open questions or assumptions for engineers to confirm. Output is passed back to the backend for inclusion in a pull request.

### GitHub integration

The backend uses a **GitHub App** to:

- Read repository contents (e.g., source and existing docs)
- Comment on issues (e.g., to link a PR or post status)
- Create branches and pull requests containing the proposed documentation changes

Details of how the agent uses the GitHub API for these operations are covered in [GitHub integration](/docs/api/github-integration).

## Data flow

```
GitHub Issue → Backend → Research Agent → Research Report
                                    ↓
              Writer Agent ← Research Report
                    ↓
              Proposed docs (files + optional questions)
                    ↓
              Backend → GitHub (new branch, PR, issue comment)
```

The backend is the single point of integration with GitHub and the only component that triggers or waits on the agents. The frontend is stateless with respect to the pipeline; it only invokes backend endpoints and displays results.
