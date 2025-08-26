# Developer and Integration Guide

## Overview
Guidance for extending, integrating, and developing against NeoV3 components.

## APIs
- API service located at `api/`.
- Refer to `documentation/api/README.md` and tests in `tests/api/` for endpoints and expected behaviors.
- Health: `/health`. Metrics (if exposed): `/metrics`.

### API Reference (OpenAPI/Redoc)
- Generated spec: `documentation/api/openapi.json`
- Human-friendly docs: open `documentation/api/redoc.html` in a browser
- Generate/refresh the spec locally:
```
python scripts/docs/generate_openapi.py --out documentation/api/openapi.json
```
Notes:
- The generator imports the Flask app (`api/app.py`) and extracts the Flask-RESTX schema.
- Ensure dependencies are installed and environment variables for the app are sane for local generation.

## SDKs & Clients
- REST: any HTTP client. Example with curl:
```
curl -s http://<host>/health
```
- WebSocket or streaming endpoints documented in API README (if enabled).

## Integration Patterns
- Message-driven via RabbitMQ (`RABBITMQ_URL`), agents publish/subscribe.
- Database integration via API; direct DB access discouraged in integrations.

## Extending the System
- Add new agent:
  - Create K8s deployment + service in `infrastructure/k8s/base/` and include in `kustomization.yaml`.
  - Parameterize image in base/overlays images list.
  - Add monitoring (ServiceMonitor) if needed.
- Add new API endpoints:
  - Implement in `api/` with tests under `tests/api/`.
  - Update OpenAPI docs if maintained.

## Configuration & Environments
- Use Kustomize overlays (`overlays/dev`, `overlays/prod`) for env-specific config.
- Images overridden by CI via `kustomize edit set image`.

## Coding Standards
- Follow `documentation/developer-guides/CONTENT_QUALITY_STANDARDS.md`.
- Add tests for features (`tests/`), ensure lint/test in CI (see `.github/workflows/ci.yml`).

## Examples
- Deploy locally to K8s dev overlay:
```
kubectl apply -k infrastructure/k8s/overlays/dev
```
- Override image in CI:
```
kustomize edit set image neov3/api=neov3/api:<tag>
```

## Security & Access Control
- RBAC definitions: `infrastructure/security/rbac/policies.yaml`.
- ABAC logic: `api/security/policy.py` comparators and logical operators.

## Observability
- Add metrics endpoints and annotate services for Prometheus scraping.
- Logs and traces through OTEL if enabled.

## Contributing
- Branching strategy, PR reviews, CI status checks.
- Ensure deployments and validation pass prior to merge.
