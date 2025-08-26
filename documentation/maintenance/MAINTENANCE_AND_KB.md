# Maintenance Procedures and Knowledge Base

## Maintenance Procedures
- Versioning and Releases
  - Use immutable image tags (commit SHA) for traceability.
  - Update overlays via CI setting images.
- Dependency Updates
  - Regularly update base images and libraries; verify in dev before prod.
- Backups
  - Database backups per org policy; see `scripts/backup/` for examples.
- Security
  - Periodically review RBAC and ABAC rules.
  - Rotate keys per `KEY_ROTATION_DAYS` policy.

## Knowledge Base (FAQ)
- Deployment fails at rollout
  - Check `kubectl describe deploy/api-service` for events.
  - Inspect container logs for errors.
- Health check failing
  - Use port-forward in `validate.sh` and verify `/health`.
- Metrics not visible
  - Ensure ServiceMonitor deployed and labels match Prometheus operator.
- How to rollback in prod
  - Re-run deploy workflow with `approve_rollback=true`.

## Documentation Maintenance
- Keep docs aligned with code changes (PR checklist item).
- Update diagrams and paths when refactoring.
- Schedule quarterly documentation review.
