# Operations Guide

This guide covers day-2 operations: deploy, scale, backup/restore, and incident response.

## Deployments
- Config via `.env` (see `documentation/configuration/ENVIRONMENT_CONFIG.md`).
- Reverse proxy (nginx/traefik) terminates TLS; API runs behind it.
- DB migrations: apply via your chosen tool (Alembic recommended; not included yet).

## Scaling
- API: horizontal scale behind load balancer; enable sticky sessions for Socket.IO or use Redis message queue.
- DB: tune pool (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`); monitor slow queries.
- Queues: RabbitMQ clustering or managed service.

## Backups & DR
- DB backups: `scripts/backup/backup-db.*` (ensure `DATABASE_URL`).
- Object storage snapshots: S3/GCS/Azure as applicable.
- DR: document RPO/RTO, practice restores regularly.

## Maintenance
- Temp cleanup: `scripts/maintenance/cleanup-temp.*`
- Rotate logs with platform tools or container log drivers.

## Monitoring & Alerting
- Prometheus/Grafana/Alertmanager setup in `infrastructure/monitoring/`.
- Sentry and OTEL optional.

## Security
- JWT secrets rotated regularly; use secret managers.
- Enable TLS everywhere; validate SSL for DB/Neo4j.
- Run periodic scans (Trivy/ZAP) under `tests/security/`.

## Incident Response
- See `workflows/security/incident_response.md`.
- Keep runbooks up to date with contacts and escalation paths.
