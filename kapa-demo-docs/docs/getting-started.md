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

| Directory            | Purpose |
|----------------------|--------|
| `kapa-demo/`         | Next.js app for the dashboard, coverage gaps, issues, fixes, and fix chat |
| `kapa_demo_backend/` | Django service that runs the research and writer agents and talks to GitHub |
| `kapa-demo-docs/`    | This documentation site (Docusaurus); the agent can propose changes here |

## Quick start

### 1. Clone and install

```bash
git clone <repository-url>
cd kapa-agent
```

Install backend dependencies:

```bash
cd kapa_demo_backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd ../kapa-demo
npm install
```

### 2. Configure environment

Copy the example environment file and set your values:

```bash
cp kapa_demo_backend/env.example.txt kapa_demo_backend/.env
```

Edit `kapa_demo_backend/.env` and set at least:

- GitHub App credentials (used by the backend for repository access and PR creation)
- OpenAI API key for the research and writer agents

The frontend may need a `.env.local` with the backend URL if you run them separately.

### 3. Run the backend

From the project root:

```bash
cd kapa_demo_backend
source .venv/bin/activate
python manage.py migrate
python manage.py load_sample_data
python manage.py runserver
```

The API is available at `http://localhost:8000` by default. `load_sample_data` seeds five coverage gaps for the demo.

### 4. Run the frontend

In a separate terminal:

```bash
cd kapa-demo
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

## Resetting demo data

To clear all demo data (including GitHub installations) and start fresh:

```bash
cd kapa_demo_backend
python manage.py load_sample_data --clear
python manage.py load_sample_data
```

## Next steps

- Read [Architecture overview](/docs/architecture/overview) to understand how the system is structured.
- See [Backend API](/docs/api/backend-api) for available endpoints.
- See [GitHub integration](/docs/api/github-integration) for how the agent interacts with GitHub.
