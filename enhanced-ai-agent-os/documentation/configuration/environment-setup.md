# Environment Configuration Setup

This guide explains how to configure the Enhanced AI Agent OS across development and production environments, covering AI providers, security, monitoring, and optional integrations.

## Files
- `.env.example` — comprehensive template of all available settings
- `.env.development.example` — development defaults
- `.env.production.example` — production-focused defaults
- `enhanced-ai-agent-os/scripts/validate-environment.sh` — validation script

Copy one of the example files to `.env` and adjust values. Do not commit real secrets.

## Configuration Categories
- **Core**: `APP_ENV`, `N8N_BASE_URL`, `PORT`
- **Database/Cache**: `DB_TYPE`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `REDIS_URL`
- **AI Providers**: `AI_DEFAULT_PROVIDER`, `OPENAI_*`, `ANTHROPIC_*`, `GOOGLE_*`, `AZURE_OPENAI_*`
- **Security/Auth**: `JWT_SECRET`, `ENCRYPTION_KEY (base64:<32 bytes>)`, `HMAC_SECRET`, `WEBHOOK_SECRET`, CORS `ALLOW_ORIGINS`, rate-limits
- **Monitoring/Tracing**: `LOG_LEVEL`, `ENABLE_PROMETHEUS`, `PROMETHEUS_PORT`, `ENABLE_TRACING`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`
- **Alerting**: `PAGERDUTY_INTEGRATION_KEY`, `SLACK_WEBHOOK_URL`
- **External Services**: `NEO4J_*`, email provider (`EMAIL_PROVIDER` + SendGrid/SES/SMTP settings), social tokens, cloud storage (AWS/GCP/Azure)
- **Performance**: `PARALLELISM_DEFAULT`, `MAX_RETRIES_DEFAULT`, `BACKOFF_STRATEGY`, `TIMEOUT_MS`
- **Feature Flags**: `FEATURE_ENABLE_*`
- **Compliance/Governance**: `COMPLIANCE_STANDARDS`, `AUDIT_LOG_*`

## AI Provider Setup
- Set `AI_DEFAULT_PROVIDER` to one of `openai|anthropic|google|azure`.
- Provide the corresponding API keys and model/deployment names.
- For Azure, set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`.

## Security Best Practices
- **Secrets**: Use a secret manager in production (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault).
- **Encryption Key**: Provide 32 raw bytes, base64-encode, and prefix with `base64:` (e.g., `base64:...`).
- **CORS**: Restrict `ALLOW_ORIGINS` in production to trusted domains.
- **Rate Limits**: Tune `RATE_LIMIT_*` for public endpoints.
- **Audit Logs**: Enable `AUDIT_LOG_ENABLED` and choose a safe destination; centralize logs in production.

## Monitoring and Tracing
- Enable Prometheus metrics via `ENABLE_PROMETHEUS=true` and `PROMETHEUS_PORT`.
- Enable OTEL tracing with `ENABLE_TRACING=true` and set `OTEL_EXPORTER_OTLP_ENDPOINT`.

## Email Providers
- Choose `EMAIL_PROVIDER=sendgrid|ses|smtp|none` and set the relevant credentials.
- For SES, set `SES_ACCESS_KEY_ID` and `SES_SECRET_ACCESS_KEY`.
- For SMTP, set `SMTP_HOST` and `SMTP_FROM` at minimum.

## Multiple Environments
- Development: start from `.env.development.example`.
- Production: start from `.env.production.example` and harden values (CORS, secrets, tracing, Redis, etc.).
- You can keep per-environment files and load them via your process manager (e.g., Docker Compose, systemd, or CI/CD).

## Validation
Use the validator to check your `.env`:

```bash
bash enhanced-ai-agent-os/scripts/validate-environment.sh --env-file .env
```

The script ensures required values are present based on provider choices and environment. It exits non-zero on errors and prints warnings for weak defaults.

## Example Minimal Dev Configuration
```
APP_ENV=development
N8N_BASE_URL=http://localhost:5678
AI_DEFAULT_PROVIDER=openai
OPENAI_API_KEY=sk-...
JWT_SECRET=dev_secret
ENCRYPTION_KEY=base64:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
HMAC_SECRET=dev_hmac
WEBHOOK_SECRET=dev_webhook
```

## Troubleshooting
- **Validation errors**: Ensure provider-specific keys are set for the chosen `AI_DEFAULT_PROVIDER`.
- **Tracing enabled but no endpoint**: Set `OTEL_EXPORTER_OTLP_ENDPOINT` when `ENABLE_TRACING=true`.
- **Email send failures**: Confirm the provider settings match `EMAIL_PROVIDER`.
