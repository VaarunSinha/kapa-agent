# Kapa Coverage Gap Action Agent




https://github.com/user-attachments/assets/7262e1d0-56b7-450b-aed6-f66609c79e13


An AI-powered documentation assistant that turns **documentation coverage gaps** into actionable updates. The system analyzes your codebase and docs, proposes changes via research and writer agents, and opens pull requests so engineers can review and merge documentation improvements directly in GitHub.

## What it does

1. **Coverage gap** — Gaps are identified (e.g. from conversations or analytics) with a finding and suggestion.
2. **Issue** — Acting on a gap creates a GitHub issue (title, description, research goal) via the Issue Creator agent.
3. **Research** — The Research Agent uses repo context (vector search + understanding) to produce a report or ask clarifying questions.
4. **Questions** — When the agent needs input, the frontend collects answers; research is re-run with answers.
5. **Fix** — The Writer Agent drafts documentation changes (one or more files) following project style.
6. **Review** — Engineers review the proposed fix in the UI; edits can be made with the Fix Assistant.
7. **Pull request** — Approval triggers the backend to create a branch, commit the fix, and open a PR.

Contributors review the changes, edit the draft, and answer questions directly in the pull request.

## Project structure

| Directory               | Stack                                   | Description                                                                                  |
| ----------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------- |
| **`kapa-demo`**         | Next.js 16, React 19, Tailwind          | Frontend: dashboard, coverage gaps, issues, research, questions, fix preview & Fix Assistant |
| **`kapa_demo_backend`** | Django 6, Celery, Redis, Chroma, OpenAI | Backend: REST API, Celery tasks, GitHub App, research/writer/fix agents                      |
| **`kapa-demo-docs`**    | Docusaurus                              | Documentation site where the agent proposes changes (example docs repo)                      |

### Backend apps

- **`data`** — Coverage gaps list and metrics API.
- **`agent`** — Issues, research, questions, fixes, and agent orchestration (Issue Creator, Research, Writer, Fix Assistant).
- **`github`** — GitHub App: installation, webhook, repo indexing (Chroma), branches, commits, PRs.

### Agents

- **Issue Creator** — Turns a coverage gap (title, finding, suggestion) into an issue title, description, and research goal using repo understanding.
- **Research Agent** — Uses issue context and retrieved content; returns a research report or SurveyJS-style questions.
- **Writer Agent** — Consumes the research report and style guidance; produces documentation file content.
- **Fix Assistant** — Applies user edits from the UI to fix content during review.

## Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend, docs)
- **Redis** (Celery broker and result backend)
- **OpenAI API key** (agents and embeddings)
- **GitHub App** (for repo access, branches, commits, PRs) — optional for local UI; required for full flow

## Quick start

### 1. Backend

```bash
cd kapa_demo_backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
cp ../env.example.txt .env   # then edit .env
```

Edit `.env` (at least):

- `OPENAI_API_KEY` — required for agents and embeddings
- `WEBHOOK_PROXY_URL` — e.g. `https://smee.io/<your_id>` for GitHub webhooks
- `GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY` — for GitHub App (needed for install, indexing, PRs)

Start Redis, then:

```bash
# Migrations
python manage.py migrate

# Run server
python manage.py runserver
```

In another terminal (from `kapa_demo_backend` with venv active):

```bash
celery -A kapa_demo_backend worker -l info
```

### 2. Frontend

```bash
cd kapa-demo
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The app talks to the backend at `http://localhost:8000` by default; set `NEXT_PUBLIC_API_URL` if your API is elsewhere.

### 3. Docs 

```bash
cd kapa-demo-docs
npm install
npm run start
```

## Environment variables

### Backend (`kapa_demo_backend/.env`)

| Variable                | Description                                         |
| ----------------------- | --------------------------------------------------- |
| `OPENAI_API_KEY`        | **Required.** Used for embeddings and agents.       |
| `GITHUB_APP_ID`         | GitHub App ID (for installation, indexing, PRs).    |
| `GITHUB_PRIVATE_KEY`    | GitHub App private key (PEM string or path).        |
| `WEBHOOK_PROXY_URL`     | Smee (or similar) URL for GitHub webhooks.          |
| `CELERY_BROKER_URL`     | Default: `redis://localhost:6379/1`.                |
| `CELERY_RESULT_BACKEND` | Default: `redis://localhost:6379/1`.                |
| `CHROMA_PERSIST_DIR`    | Optional; default is `./chroma_data` under backend. |

### Frontend (`kapa-demo`)

| Variable              | Description                                      |
| --------------------- | ------------------------------------------------ |
| `NEXT_PUBLIC_API_URL` | Backend base URL (e.g. `http://localhost:8000`). |

## API overview

The Django backend exposes a REST API under `/api/`:

- **Coverage gaps** — `GET /api/coverage-gaps/` (metrics + list)
- **Act on gap** — `POST /api/coverage-gaps/<id>/act` (creates issue, enqueues research)
- **Issues** — `GET /api/issues/`, `GET /api/issues/<id>/`
- **Research** — `GET /api/research/`, `GET /api/research/<issue_id>/`
- **Questions** — `GET /api/questions/<research_id>/`, `POST /api/questions/submit/`
- **Fixes** — `GET /api/fixes/`, `GET /api/fixes/<id>/`, `GET /api/fixes/by-issue/<issue_id>/`, `POST /api/fixes/<id>/approve/`

GitHub: `GET/POST /api/github/installation`, `POST /api/github/webhook`; setup redirects under `/github/`.

See `kapa-demo-docs/docs/api/backend-api.md` for full API details.

## Data flow

```
Coverage Gap → Act → Issue → Research (→ Questions → Research) → Fix → Approve → PR
```

The frontend drives the flow by calling the backend API; Celery runs research and publish tasks. The backend is the single point of integration with GitHub and the only component that runs the agents.

## Purpose

This project is a **prototype** that shows how an automated documentation assistant can:

- Respond to reported documentation gaps quickly
- Keep documentation aligned with the codebase
- Produce reviewable proposals (issues, research, fixes, PRs) that engineers can edit and merge

It is suitable for evaluation, internal demos, and as a base for a production-ready documentation assistant.

## License

See [LICENSE](LICENSE) in the repository root.
