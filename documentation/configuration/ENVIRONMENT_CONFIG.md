# Environment Configuration Guide

This document describes all configuration parameters, recommended values for each environment, security best practices, deployment scenarios, and troubleshooting tips.

- File templates:
  - Development: `.env.development.example`
  - Staging: `.env.staging.example`
  - Production: `.env.production.example`
  - Cloud (managed services): `.env.cloud.example`
  - Unified superset (optional): `unified.env.example`
- Validator: `scripts/config/validate_env.py` (wrappers: `scripts/config/validate.sh`, `scripts/config/validate-staging.ps1`)

## Override hierarchy

Configuration is loaded from environment variables. We recommend the following file strategy:

1. Base file: `.env` (copied from `.env.example` or `unified.env.example`)
2. Environment-specific overrides (not committed): `.env.development`, `.env.staging`, `.env.production`, `.env.cloud`
3. Local machine overrides (ignored): `.env.local`

Precedence (highest wins) generally follows: process env vars > `.env.<environment>` > `.env`.

Security: `.gitignore` is configured to ignore `.env` and `.env.*` but keep `*.example` templates tracked.

## Environment Variables Matrix

| Name | Default | Required | Scope | Description | Example |
|---|---|---|---|---|---|
| HOST | 0.0.0.0 | no | API | Bind address for Flask/Socket.IO | 0.0.0.0 |
| PORT | 8000 | no | API | API listen port | 8000 |
| FLASK_ENV | production | no | API | Flask environment | development |
| SECRET_KEY | — | yes (prod) | API | Flask secret key | random 32+ chars |
| CORS_ORIGINS | * (dev) | no | API | Allowed origins for CORS | http://localhost:3000 |
| DATABASE_URL | — | yes | API | Postgres URL (SQLAlchemy) | postgresql+psycopg2://user:pass@postgres:5432/db |
| POSTGRES_USER | postgres | no | Postgres | Container user | ai_agent_user |
| POSTGRES_PASSWORD | — | yes | Postgres | Container password | secret |
| POSTGRES_DB | postgres | no | Postgres | Database name | enhanced_ai_os |
| NEO4J_URI | bolt://neo4j:7687 | no | API/Workers | Neo4j bolt URL | bolt://neo4j:7687 |
| NEO4J_USER | neo4j | no | API/Workers | Neo4j user | neo4j |
| NEO4J_PASSWORD | — | yes | API/Workers | Neo4j password | changeme |
| RABBITMQ_DEFAULT_USER | ai_agent_queue_user | no | RabbitMQ | Default RMQ user to provision/use | ai_agent_queue_user |
| RABBITMQ_DEFAULT_PASS | — | yes | RabbitMQ | Default RMQ user password | strongpass |
| RABBITMQ_URL | derived | yes | API/Workers | AMQP URL used by clients | amqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@rabbitmq:5672/ |
| UNSTRUCTURED_QUEUE | documents.process | no | Worker/API | Queue name for document processing | documents.process |
| OPENAI_API_KEY | — | yes if embeddings | Worker/API | API key for OpenAI | sk-... |
| OPENAI_API_BASE | https://api.openai.com/v1 | no | Worker/API | Override OpenAI base URL | custom endpoint |
| AUTONOMY_ENABLED | true | no | API | Enable autonomy services | true |
| AUTONOMY_API_EXPOSE | true | no | API | Expose `/api/autonomy/*` | true |
| AUTONOMY_DEFAULT_MONITOR_INTERVAL | 60 | no | API | Monitor interval seconds | 60 |
| AUTONOMY_SAFETY_MODE | guarded | no | API | conservative|balanced|aggressive|guarded | guarded |
| DRIFT_SCAN_INTERVAL | 300 | no | API | Drift scan interval seconds | 300 |
| HEALING_POLICY | conservative | no | API | Self-healing policy | conservative |
| ENABLE_PROMETHEUS | true | no | Infra | Enable Prometheus scraping | true |
| OTEL_EXPORTER_OTLP_ENDPOINT | http://otel-collector:4317 | no | API/Workers | OTLP endpoint | http://otel-collector:4317 |
| OTEL_SERVICE_NAME | service name | no | API/Workers | Telemetry service name | enhanced-ai-agent-api |
| GRAFANA_URL | http://grafana:3000 | no | Infra | Grafana base URL | http://grafana:3000 |
| ALERTMANAGER_URL | http://alertmanager:9093 | no | Infra | Alertmanager base URL | http://alertmanager:9093 |
| N8N_BASE_URL | http://n8n:5678 | no | n8n | n8n base URL | http://n8n:5678 |
| N8N_API_KEY | — | if used | n8n | API key for n8n | xxx |
| N8N_WEBHOOK_SECRET | — | if used | n8n | Webhook verification secret | yyy |

Notes:
- `RABBITMQ_URL` is consistently constructed from `RABBITMQ_DEFAULT_USER`/`RABBITMQ_DEFAULT_PASS` and host `rabbitmq:5672` in compose.
- Prometheus UI is mapped to host port 9464 by default (`9464->9090`).
- Health endpoint retains a back-compat route at `/system/health` (no `/api` prefix).

## Core Settings
- APP_NAME: Service name.
- APP_ENV: development | staging | production.
- PORT: API port (Flask+Socket.IO).
- LOG_LEVEL: debug | info | warn | error.
- CORS_ORIGINS: Comma-separated origins. Use "*" only in development.

## Database (PostgreSQL)
- DATABASE_URL: postgresql+psycopg2://user:pass@host:port/db
- DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DB_POOL_RECYCLE: Connection pooling.
- DATABASE_SSL_MODE: disable | require | verify-ca | verify-full (prod: require+).
- DATABASE_SSL_ROOT_CERT: CA path when using verify modes.

## Redis
- REDIS_URL: redis://host:port[/db]

## RabbitMQ
- RABBITMQ_URL: amqp(s)://user:pass@host:port/vhost

### Autonomy exchanges/queues (reference)
Autonomous services use topic exchanges and DLQs defined in `infrastructure/rabbitmq/definitions.json`:
- Exchanges: `agents.lifecycle`, `agents.health`, `agents.drift`, `dead-letter.exchange`
- Queues: `agents.lifecycle.events`, `agents.health.metrics`, `agents.drift.alerts` with DLQs for each
Bindings use routing keys `lifecycle.*`, `health.*`, `drift.*` respectively.

## n8n Integration
- N8N_BASE_URL: Base URL of n8n instance.
- N8N_API_KEY: API Key for authenticated calls.
- N8N_WEBHOOK_SECRET: Secret for verifying inbound webhooks.

## JWT and Security
- JWT_SECRET / JWT_SECRET_KEY: Secret used for signing JWTs.
- ENCRYPTION_KEY: Base64-encoded 32-byte encryption key (prefix with base64:).
- HMAC_SECRET: For webhook signing.
- WEBHOOK_SECRET: Shared secret for inbound webhook validation.
- TLS_ENABLED, TLS_CERT_FILE, TLS_KEY_FILE, TLS_MIN_VERSION: TLS settings (typically at reverse proxy).

## AI Providers
- AI_DEFAULT_PROVIDER: openai | anthropic | google | azure_openai
- OPENAI_API_KEY, OPENAI_MODEL
- ANTHROPIC_API_KEY, ANTHROPIC_MODEL
- GOOGLE_API_KEY, GOOGLE_MODEL
- AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT

## Neo4j
- NEO4J_URI: bolt://host:7687 (or bolt+s:// for TLS)
- NEO4J_USER, NEO4J_PASSWORD

## Email & Notifications
- EMAIL_PROVIDER: none | sendgrid | ses | smtp
- SENDGRID_API_KEY | SES_* | SMTP_* (host, port, user, password, from)
- SLACK_WEBHOOK_URL, PAGERDUTY_INTEGRATION_KEY

## Cloud Storage
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET
- GCP_PROJECT_ID, GCP_CREDENTIALS_JSON
- AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY, AZURE_STORAGE_CONTAINER

## Observability
- ENABLE_PROMETHEUS, PROMETHEUS_PORT
- ENABLE_TRACING, OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME
- SENTRY_DSN, GRAFANA_URL, ALERTMANAGER_URL

## Features & Runtime
- PARALLELISM_DEFAULT, MAX_RETRIES_DEFAULT, BACKOFF_STRATEGY, TIMEOUT_MS
- FEATURE_ENABLE_* toggles

### Autonomy
- AUTONOMY_ENABLED: true|false — Enable agent lifecycle/drift monitors and endpoints
- AUTONOMY_API_EXPOSE: true|false — Expose `/api/autonomy/*` endpoints (if feature gated)
- AUTONOMY_DEFAULT_MONITOR_INTERVAL: integer seconds (e.g., 30)
- AUTONOMY_SAFETY_MODE: conservative|balanced|aggressive — governs self-healing decision thresholds
- DRIFT_SCAN_INTERVAL: integer seconds (e.g., 300)
- HEALING_POLICY: e.g., restart_then_roll_back | restart_only | manual

## Compliance & Auditing
- COMPLIANCE_STANDARDS: e.g., CAN-SPAM,GDPR,OWASP
- AUDIT_LOG_ENABLED, AUDIT_LOG_DESTINATION (stdout|http|file), AUDIT_LOG_PATH

## Auth / OIDC
- AUTH_PROVIDER: local | oidc
- OIDC_ISSUER, OIDC_CLIENT_ID, OIDC_CLIENT_SECRET, OIDC_AUDIENCE, OIDC_JWKS_URI

## Backups & DR
- BACKUP_ENABLED, BACKUP_S3_BUCKET, BACKUP_SCHEDULE_CRON, BACKUP_RETENTION_DAYS, DR_STRATEGY

---

# Deployment Scenarios

## Single-Server (All-in-one)
- Use local Postgres/Redis/RabbitMQ/Neo4j containers.
- CORS_ORIGINS can include localhost URLs.
- TLS typically terminated by reverse proxy (nginx/traefik).

## Multi-Server (On-prem)
- Externalize DB, Redis, RabbitMQ, Neo4j to dedicated hosts.
- Enable TLS for DB/Neo4j (verify modes), restrict CORS.
- Configure centralized logging and tracing.

## Cloud-Based (Managed Services)
- Use managed Postgres (RDS/Cloud SQL), Redis (Elasticache/Memorystore), MQ (RMQ Cloud), Neo4j Aura.
- Leverage cloud secret managers (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault).
- Backups via managed snapshots and S3/GCS/Azure Blob.

Use `.env.cloud` or platform env vars. The cloud migration scripts read:

- Postgres: `DATABASE_URL` (preferred) or `DB_*` components
- Neo4j: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

---

# Security Best Practices
- Never commit secrets. Use docker/k8s secrets or cloud secret managers.
- Rotate keys regularly; enforce TLS for all external comms.
- Restrict CORS in production. Set strong JWT secret (>32 bytes).
- Use least privilege IAM for cloud resources.
- Prefer network policies and VPC peering for data stores.

---

# Validation
Run the validator to check required variables and formats:

- Development:
```
python scripts/config/validate_env.py --env-file .env.development.example --environment development
```
- Staging:
```
python scripts/config/validate_env.py --env-file .env.staging.example --environment staging
```
- Production:
```
python scripts/config/validate_env.py --env-file .env.production.example --environment production
```
 - Bash wrapper:
```
scripts/config/validate.sh .env.staging.example staging
```
 - PowerShell (staging):
```
powershell -File scripts/config/validate-staging.ps1 -EnvFile .env.staging.example
```

Exit code 0 indicates success; non-zero indicates missing or invalid settings.

---

# Troubleshooting
- DB connection errors: verify DATABASE_URL, network reachability, SSL mode and CA.
- CORS blocked: set CORS_ORIGINS correctly and include your frontend origin.
- Neo4j TLS: use bolt+s:// and ensure certificates are trusted.
- n8n webhooks: ensure N8N_BASE_URL public URL and matching N8N_WEBHOOK_SECRET.
- JWT invalid/expired: verify JWT_SECRET and client Bearer headers.
- RabbitMQ authentication failure: check RABBITMQ_URL and vhost permissions.
