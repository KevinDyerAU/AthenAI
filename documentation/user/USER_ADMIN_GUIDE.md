# User and Administrator Guide

## For Users
- Access the API via the provided base URL.
- Check system health at `/health`.
- Use documented API endpoints to interact with agents and data.

### Tutorials
- Getting Started:
  1) Obtain API base URL and auth if required.
  2) Call `/health` to verify availability.
  3) Use sample requests from `documentation/api/README.md`.

## For Administrators
- Deployments
  - Use Kustomize overlays: `infrastructure/k8s/overlays/dev|prod`.
  - CI workflow `.github/workflows/deploy.yml` with manual approval for prod.
- Configuration
  - Edit `configmap.yaml` and overlay patches as needed.
  - Secrets via K8s Secrets/External manager.
- Monitoring
  - Prometheus/Grafana via addon and dashboards; check ServiceMonitor.
- Performance
  - Tune HPA (`hpa.yaml`), resource requests/limits in deployments.
- Security
  - Follow RBAC/ABAC policies, sandbox constraints in deployments.

## Troubleshooting
- Run `scripts/deploy/validate.sh <namespace> api-service 18080` to validate.
- Inspect pod logs: `kubectl -n <ns> logs deploy/api-service`.
- Common issues:
  - Image tag mismatch → verify CI set images and registry auth.
  - Health failing → port-forward and try `/health`.
  - RBAC denied → review `policies.yaml` and roles.

## Maintenance
- Rolling updates via new image tags and `kubectl rollout status`.
- Rollback (prod): rerun workflow with `approve_rollback=true`.
