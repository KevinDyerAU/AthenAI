#!/usr/bin/env bash
set -euo pipefail

# validate-environment.sh --env-file <path>
# Validates required configuration for Enhanced AI Agent OS across providers and services.

ENV_FILE=".env"
if [[ ${1:-} == "--env-file" && -n ${2:-} ]]; then
  ENV_FILE="$2"
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "[ERROR] Env file not found: $ENV_FILE" >&2
  exit 2
fi

# Load .env safely (basic parser: KEY=VALUE, ignores comments/blank)
while IFS= read -r line; do
  [[ -z "$line" || "$line" =~ ^\s*# ]] && continue
  if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
    key="${line%%=*}"
    val="${line#*=}"
    # strip surrounding quotes if present
    val="${val%\r}"
    val="${val#\"}"; val="${val%\"}"
    val="${val#\'}"; val="${val%\'}"
    export "$key"="$val"
  fi
done < "$ENV_FILE"

errors=0
warn() { echo "[WARN] $1"; }
err() { echo "[ERROR] $1"; errors=$((errors+1)); }
ok() { echo "[OK] $1"; }

# Core
[[ -n "${APP_ENV:-}" ]] || err "APP_ENV is required (development|staging|production)"
[[ -n "${N8N_BASE_URL:-}" ]] || err "N8N_BASE_URL is required"

# Database
if [[ "${DB_TYPE:-postgres}" != "sqlite" ]]; then
  [[ -n "${DB_HOST:-}" ]] || err "DB_HOST required for DB_TYPE=$DB_TYPE"
  [[ -n "${DB_PORT:-}" ]] || err "DB_PORT required for DB_TYPE=$DB_TYPE"
  [[ -n "${DB_USER:-}" ]] || err "DB_USER required for DB_TYPE=$DB_TYPE"
  [[ -n "${DB_NAME:-}" ]] || err "DB_NAME required for DB_TYPE=$DB_TYPE"
  if [[ "${APP_ENV:-}" == "production" ]]; then
    [[ -n "${DB_PASSWORD:-}" ]] || err "DB_PASSWORD required in production"
  fi
fi

# Security
[[ -n "${JWT_SECRET:-}" ]] || err "JWT_SECRET is required"
if [[ -z "${ENCRYPTION_KEY:-}" ]]; then
  err "ENCRYPTION_KEY is required (base64:...)"
else
  if [[ ! "$ENCRYPTION_KEY" =~ ^base64: ]]; then
    warn "ENCRYPTION_KEY should be base64-prefixed (base64:<value>)."
  fi
fi
[[ -n "${HMAC_SECRET:-}" ]] || err "HMAC_SECRET is required"
[[ -n "${WEBHOOK_SECRET:-}" ]] || err "WEBHOOK_SECRET is required"

# AI Providers
prov="${AI_DEFAULT_PROVIDER:-openai}"
case "$prov" in
  openai)
    [[ -n "${OPENAI_API_KEY:-}" ]] || err "OPENAI_API_KEY required for AI_DEFAULT_PROVIDER=openai"
    ;;
  anthropic)
    [[ -n "${ANTHROPIC_API_KEY:-}" ]] || err "ANTHROPIC_API_KEY required for AI_DEFAULT_PROVIDER=anthropic"
    ;;
  google)
    [[ -n "${GOOGLE_API_KEY:-}" ]] || err "GOOGLE_API_KEY required for AI_DEFAULT_PROVIDER=google"
    ;;
  azure)
    [[ -n "${AZURE_OPENAI_ENDPOINT:-}" ]] || err "AZURE_OPENAI_ENDPOINT required for AI_DEFAULT_PROVIDER=azure"
    [[ -n "${AZURE_OPENAI_API_KEY:-}" ]] || err "AZURE_OPENAI_API_KEY required for AI_DEFAULT_PROVIDER=azure"
    ;;
  *) warn "Unknown AI_DEFAULT_PROVIDER=$prov" ;;
esac

# Monitoring / Tracing
if [[ "${ENABLE_TRACING:-false}" == "true" ]]; then
  [[ -n "${OTEL_EXPORTER_OTLP_ENDPOINT:-}" ]] || err "OTEL_EXPORTER_OTLP_ENDPOINT required when ENABLE_TRACING=true"
fi

# Email Providers
case "${EMAIL_PROVIDER:-none}" in
  sendgrid)
    [[ -n "${SENDGRID_API_KEY:-}" ]] || err "SENDGRID_API_KEY required for EMAIL_PROVIDER=sendgrid"
    ;;
  ses)
    [[ -n "${SES_ACCESS_KEY_ID:-}" && -n "${SES_SECRET_ACCESS_KEY:-}" ]] || err "SES_ACCESS_KEY_ID and SES_SECRET_ACCESS_KEY required for EMAIL_PROVIDER=ses"
    ;;
  smtp)
    [[ -n "${SMTP_HOST:-}" && -n "${SMTP_FROM:-}" ]] || err "SMTP_HOST and SMTP_FROM required for EMAIL_PROVIDER=smtp"
    ;;
  none) : ;;
  *) warn "Unknown EMAIL_PROVIDER=$EMAIL_PROVIDER" ;;
esac

# Compliance
if [[ -z "${COMPLIANCE_STANDARDS:-}" ]]; then
  warn "COMPLIANCE_STANDARDS not set; default policies may be applied"
fi

# Sensible warnings for defaults
for v in DB_PASSWORD NEO4J_PASSWORD JWT_SECRET HMAC_SECRET WEBHOOK_SECRET; do
  val="${!v:-}"
  if [[ "$val" =~ ^(change_me|dev_|test_|password)$ ]]; then
    warn "$v uses a weak default; change before production"
  fi
done

if [[ $errors -gt 0 ]]; then
  echo "\nValidation completed with $errors error(s)." >&2
  exit 1
else
  ok "Environment validation passed."
fi
