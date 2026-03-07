---
sidebar_position: 2
title: GitHub Integration
---

# GitHub Integration

The backend uses a **GitHub App** to read repository content, comment on issues, and create pull requests. The app is the single identity used for all GitHub operations performed by the agent.

## Capabilities

The integration supports:

- **Reading the repository** — Fetching file contents, directory listings, and branch information so the research agent can analyze the codebase and the writer can align with existing documentation structure.
- **Commenting on issues** — Posting status updates or linking to the created pull request on the original issue.
- **Creating pull requests** — Pushing a new branch with the proposed documentation changes and opening a PR. The PR description can include open questions for engineers.

Once the app is installed on a repository or organization, the backend performs these actions in the context of the installation.

## Typical workflow

1. A user acts on a coverage gap from the frontend; the backend creates an issue and starts research.
2. When research needs repo content, the backend uses the app to fetch files and tree information.
3. After the Writer Agent produces the draft, the backend creates a new branch, commits the doc changes, and opens a pull request.
4. Optionally, the backend posts a comment on the original issue with a link to the PR.

No user OAuth is required for the agent to operate once the app is installed.

## Permissions

The GitHub App must be granted:

- **Repository contents** — Read (and Write when creating branches and commits)
- **Pull requests** — Read and Write (to create and update PRs)
- **Issues** — Read and Write (to read issue content and add comments)
- **Metadata** — Read (required for repository access)

These are configured in the GitHub App settings. Restrict the app to the repositories that are allowed to use the documentation agent.

## Branch and PR naming

- **Branch** — Created from the base branch (e.g., `main`). Name follows a pattern like `docs/issue-{number}-content-gap` so it is clear which issue the change addresses.
- **PR title** — Derived from the issue title (e.g., "Docs: Add API authentication section").
- **PR body** — Includes a short summary, a link back to the issue, and optionally the list of open questions from the writer agent for engineers to address.

Engineers review the PR as they would any other change; they can push additional commits to the same branch or close the PR and apply changes manually.
