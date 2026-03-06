---
sidebar_position: 2
title: Getting Started
---

# Getting Started

This guide walks you through running the Kapa Content Gap Action Agent locally.

## Prerequisites

- **Node.js** 18+ (for the Next.js frontend)
- **Python** 3.10+ (for the Django backend)
- **Git** (for repository access and PR creation)
- A **GitHub repository** that the agent will analyze and where it will open pull requests

## Repository layout

The project is split into three main areas:

| Directory   | Purpose |
|------------|---------|
| `frontend/` | Next.js app for triggering documentation tasks and viewing status |
| `backend/`  | Django service that runs the research and writer agents and talks to GitHub |
| `docs/`     | This documentation site; the agent can propose changes here |

## Quick start

### 1. Clone and install

```bash
git clone <repository-url>
cd kapa-agent
```

Install backend dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd ../frontend
npm install
```

### 2. Configure environment

Copy the example environment file and set your values:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set at least:

- GitHub App credentials or token (used by the backend for repository access and PR creation)
- Any API keys required by the research or writer services

The frontend may need a `.env.local` with the backend URL if you run them separately.

### 3. Run the backend

From the project root:

```bash
cd backend
source .venv/bin/activate
python manage.py runserver
```

The API is available at `http://localhost:8000` by default.

### 4. Run the frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` to use the UI.

### 5. Run the documentation site (Docusaurus)

To view this documentation locally:

```bash
cd kapa-demo-docs
npm install
npm run start
```

The docs site is served at `http://localhost:3000` (or the next free port if 3000 is in use). Use a different port if the main frontend is already running.

## Next steps

- Read [Architecture overview](/docs/architecture/overview) to understand how the system is structured.
- See [Backend API](/docs/api/backend-api) for available endpoints.
- See [GitHub integration](/docs/api/github-integration) for how the agent interacts with GitHub.
