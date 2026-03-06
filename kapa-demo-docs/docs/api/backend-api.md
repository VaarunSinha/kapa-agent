---
sidebar_position: 1
title: Backend API
---

# Backend API

The Django backend exposes a REST API used by the frontend and, optionally, by webhooks or other automation. All endpoints are prefixed with `/api/` unless otherwise noted.

## Base URL

When running locally, the API is available at `http://localhost:8000`. The frontend is configured to use this base URL in development; for production, set the appropriate backend URL in the frontend environment.

## Authentication

API requests use token-based authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-token>
```

Tokens are issued by the backend (e.g., via an admin or a dedicated token endpoint). Unauthenticated requests to protected endpoints return `401 Unauthorized`.

## Endpoints

### Task status

**`GET /api/tasks/{task_id}/`**

Returns the current status and result of a documentation task. Used by the frontend to poll for completion and to retrieve the pull request URL or error message.

**Response (200):**

```json
{
  "id": "uuid",
  "status": "pending|running|completed|failed",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "result": {
    "pull_request_url": "https://github.com/org/repo/pull/123",
    "branch": "docs/issue-42-content-gap"
  },
  "error": null
}
```

If `status` is `failed`, `error` contains a short message describing the failure.

---

### Create documentation task

**`POST /api/tasks/`**

Creates a new documentation task. The request body must include the GitHub issue URL or repository and issue number so the backend can fetch the issue and run the pipeline.

**Request body:**

```json
{
  "issue_url": "https://github.com/org/repo/issues/42",
  "branch": "main"
}
```

`branch` is optional and defaults to the repository's default branch. It indicates the base branch for the documentation PR.

**Response (201):**

```json
{
  "id": "uuid",
  "status": "pending",
  "created_at": "ISO8601"
}
```

The task runs asynchronously. Poll `GET /api/tasks/{id}/` for status and result.

---

### Trigger documentation research

For debugging or internal tooling, the backend exposes an endpoint that runs only the research phase of the pipeline. This starts the research agent for the given issue and repository and returns when the research report is ready. It does not run the writer agent or create a pull request. The endpoint is intended for inspecting research output or validating repository access. Request and response formats are consistent with the rest of the API; see the task creation endpoint for how to supply issue and repository context.

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

- **400 Bad Request**: Invalid request body or parameters. The response body includes a JSON object with field-level errors.
- **401 Unauthorized**: Missing or invalid authentication token.
- **404 Not Found**: Task ID or resource does not exist.
- **500 Internal Server Error**: Server error. Check backend logs for details.

## Rate limits

In the current prototype, no rate limiting is applied. For production, consider rate limiting per token or per IP to avoid abuse and to stay within external API (e.g., GitHub, LLM provider) limits.
