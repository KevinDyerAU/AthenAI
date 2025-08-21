# Environment Configuration Guide

This document describes all configuration parameters, recommended values for each environment, security best practices, deployment scenarios, and troubleshooting tips.

- File templates:
  - Development: `.env.development.example`
  - Production: `.env.production.example`
- Validator: `scripts/config/validate_env.py`

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
- Production:
```
python scripts/config/validate_env.py --env-file .env.production.example --environment production
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
