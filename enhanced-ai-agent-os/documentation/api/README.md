# Enhanced AI Agent OS API

This documentation describes the REST and webhook interfaces for integrating with the Enhanced AI Agent OS running on n8n.

- Base URL (local): `http://localhost:5678`
- OpenAPI spec: `api/openapi.yaml`

## Contents
- Authentication and authorization
- Endpoints overview
- Webhook payloads and responses
- Rate limiting and usage policy
- Versioning and deprecation
- Integration examples
- Testing and validation tools

---

## Authentication and Authorization

Supported authentication methods:

- API Key (header): `X-N8N-API-KEY: <token>`
- HTTP Basic Auth: `Authorization: Basic <base64(user:pass)>`

Guidance:
- Prefer API keys for service-to-service integrations.
- Use HTTPS in production.
- Do not hardcode secrets; use environment variables or secret stores.

---

## Endpoints Overview

- `GET /rest/workflows` — List workflows
- `POST /rest/workflows` — Create workflow
- `GET /rest/workflows/{id}` — Get workflow
- `POST /rest/workflows/{id}/activate` — Activate/deactivate workflow

Agent webhooks:
- `POST /webhook/planning-agent`
- `POST /webhook/execution-agent`
- `POST /webhook/quality-assurance-agent`

Health:
- `GET /health`

See full schema and examples in `api/openapi.yaml`.

---

## Webhook Payloads and Responses

- Planning request fields: `project`, `tasks`, `resources`
- Execution request fields: `tasks` (with `deps`), `concurrency`
- QA request fields: `artifacts`, `standards`

Responses generally include a `status` field (e.g., `ok`) and a result object such as `plan`, `batches`, or `qualityReport`.

---

## Rate Limiting and Usage Policy

- Default policy: 60 requests/minute per API key, per IP (example baseline).
- Exceeding the limit returns `429 Too Many Requests` with a `Retry-After` header.
- Backoff: Use exponential backoff with jitter.
- Long-running jobs: Prefer asynchronous patterns, webhooks, or polling endpoints.

Note: Actual enforcement depends on your deployment gateway (e.g., API Gateway/Ingress). Configure and document concrete limits in production.

---

## Versioning and Deprecation

- URI versioning: `v1` in the `info.version` of OpenAPI; future breaking changes increment major.
- Minor/patch changes are backward compatible.
- Deprecations are announced in release notes and `Deprecation` headers where applicable.
- Sunset policy: Minimum 90 days notice before removal of deprecated endpoints.

---

## Integration Examples

See `examples/integrations/` for:
- Python (`requests`)
- Node.js (native `fetch` / undici)
- cURL scripts

---

## Testing and Validation Tools

- Validate spec: `tests/api/run-api-tests.sh --validate-spec`
- Smoke test endpoints: `tests/api/run-api-tests.sh --smoke`
- Performance tests: `enhanced-ai-agent-os/tests/performance/test-endpoints-load.sh`

Prerequisites:
- `curl`, `jq`
- Optional: `docker` (for swagger-cli), `k6`, `ab`

---

## Troubleshooting

- 401/403: Verify `X-N8N-API-KEY` or Basic Auth credentials.
- 404: Confirm endpoint path and active workflow.
- 429: Apply retry with backoff; review rate limits.
- 5xx: Check n8n logs and upstream services.

For more, see `documentation/developer-guides/troubleshooting.md`.
