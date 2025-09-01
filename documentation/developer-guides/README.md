# Developer Guides

This section aggregates guides for extending and integrating NeoV3.

- See `DEVELOPER_INTEGRATION_GUIDE.md` for integration steps and patterns.
- See `CONTENT_QUALITY_STANDARDS.md` for documentation and code quality standards.

## Environment references
- All environment variables used by services are documented in `documentation/configuration/ENVIRONMENT_CONFIG.md`.
- Quick summary is in `documentation/configuration/README.md`.

## API base and routes
- Base REST API path: `/api` (set via `api/extensions.py`).
- Docs: `/api/docs` (Swagger UI), `/redoc` (ReDoc), `/api/swagger.json` (spec).
- Example ingestion endpoint: `POST /api/documents/enqueue`.

## Local development
- Start: `./deploy-local.sh --fresh` (or PowerShell equivalents).
- Status: `./deploy-local.sh --status`.
- Logs: `docker logs -f enhanced-ai-agent-api`.
