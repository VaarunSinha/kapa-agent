---
sidebar_position: 1
title: Backend API
---

# Backend API

The Django backend exposes a REST API used by the frontend. All endpoints are prefixed with `/api/` unless otherwise noted.

## Base URL

When running locally, the API is available at `http://localhost:8000`. The frontend is configured to use this base URL in development; for production, set the appropriate backend URL in the frontend environment.

## Authentication

API requests use token-based authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-token>
```

Tokens are issued by the backend (e.g., via an admin or a dedicated token endpoint). Unauthenticated requests to protected endpoints return `401 Unauthorized`.

## Endpoints

### Coverage gaps

**`GET /api/coverage-gaps/`**

Returns metrics and the list of coverage gaps. Response includes `conversationsProcessed`, `coverageGapsIdentified`, `githubInstallUrl`, `hasConnectedRepo`, `connectedRepo`, `sourceStatus`, and `gaps` (array of coverage gap objects with id, title, conversation_count, finding, suggestion, status).

---

### Act on coverage gap

**`POST /api/coverage-gaps/<id>/act`**

Creates an Issue from the coverage gap (Issue Creator agent) and enqueues the research task. Request body is not required. Response (201): `{"issue_id": "uuid"}`.

---

### Issues

**`GET /api/issues/`** — List all issues.

**`GET /api/issues/<id>/`** — Issue detail (with related research and fixes).

---

### Research

**`GET /api/research/`** — List all research tasks.

**`GET /api/research/<issue_id>/`** — Research for the given issue (returns the latest research record for that issue).

---

### Questions

**`GET /api/questions/<research_id>/`** — List questions for the research. Response: `{"research_id": "uuid", "questions": [...]}`.

**`POST /api/questions/submit/`** — Save answers. Body: `{"answers": [...]}` (list of `{"question_id": "uuid", "answer": "..."}`) or `{"answers": {"question_id": "answer", ...}}`. After saving, the backend re-queues the research task.

---

### Fixes

**`GET /api/fixes/`** — List all fixes.

**`GET /api/fixes/<id>/`** — Fix detail (files, patch, summary, status, branch_name, pr_url, etc.).

**`GET /api/fixes/by-issue/<issue_id>/`** — Fixes for the given issue.

**`POST /api/fixes/<id>/approve/`** — Mark the fix as approved and enqueue the publish task. Response: `{"status": "ok", "fix_id": "uuid"}`.

Fixes can be edited in the UI.

---

### Health check

**`GET /api/health/`**

Returns service health. Useful for load balancers and monitoring.

**Response (200):**

```json
{
  "status": "ok"
}
```

## Error responses

- **400 Bad Request** — Invalid request body or parameters. The response body includes a JSON object with field-level errors.
- **401 Unauthorized** — Missing or invalid authentication token.
- **404 Not Found** — Resource does not exist.
- **500 Internal Server Error** — Server error. Check backend logs for details.

## Rate limits

In the current prototype, no rate limiting is applied. For production, consider rate limiting per token or per IP to avoid abuse and to stay within external API (e.g., GitHub, LLM provider) limits.
