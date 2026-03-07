---
sidebar_position: 4
title: Contributing
---

# Contributing

Contributions to the Kapa Content Gap Action Agent are welcome. This document covers how to set up a development environment and the conventions used in the project.

## Development setup

Follow the [Getting Started](/docs/getting-started) guide to clone the repo, install dependencies, and run the frontend and backend locally. Use a separate Python virtual environment and Node installation for the docs site if you are editing documentation.

## Code structure

- **Backend**: Django apps under `kapa_demo_backend/`. Agent orchestration, GitHub client, and API views live here. Keep business logic in services or dedicated modules rather than in views.
- **Frontend**: Next.js under `kapa-demo/`. Pages and components call the backend API; no direct GitHub or agent calls from the client.
- **Docs**: Markdown in `kapa-demo-docs/docs/` (this site). The agent may propose changes here; keep structure and frontmatter consistent for Docusaurus.

## Running tests

**Backend:**

```bash
cd kapa_demo_backend
source .venv/bin/activate
python manage.py test
```

**Frontend:**

```bash
cd kapa-demo
npm test
```

Add tests for new API endpoints and for agent pipeline behavior where possible. Integration tests that mock the GitHub API are in the backend test suite.

## Submitting changes

1. Open an issue or pick an existing one to link your work to.
2. Create a branch from `main` (e.g., `feature/short-description` or `fix/issue-123`).
3. Make your changes, add or update tests, and ensure the test suite passes.
4. Push the branch and open a pull request. Describe what changed and reference any related issues.
5. Address review feedback. Once approved, a maintainer will merge.

## Documentation

When adding or changing features that affect users or operators:

- Update the relevant docs under `kapa-demo-docs/docs/`. Use the same tone and structure as the rest of the set (clear, concise, no placeholders in published content).
- If you add a new API endpoint, document it in [Backend API](/docs/api/backend-api) with method, path, request body, and response format.
- For architecture or agent behavior changes, update [Architecture overview](/docs/architecture/overview) or [Agents](/docs/architecture/agents) as needed.

## Code style

- **Python**: Follow PEP 8. Use Black for formatting and run it before committing (e.g., `black kapa_demo_backend/`).
- **JavaScript/TypeScript**: Use the project's ESLint and Prettier config. Run `npm run lint` in the frontend before submitting.
- **Markdown**: Use standard Markdown and Docusaurus frontmatter. Keep line length reasonable for diffs (e.g., wrap at 100 characters where it doesn't hurt readability).

## Questions

For questions about the design or roadmap, open a GitHub discussion or an issue. For bugs or feature requests, use the issue tracker with the appropriate labels.
