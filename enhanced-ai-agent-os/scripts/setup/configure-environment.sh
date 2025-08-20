#!/usr/bin/env bash
set -euo pipefail

# configure-environment.sh
# Copies an example env file to .env, merges overrides, and validates.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

usage() {
  cat <<USAGE
Usage: $0 [--env development|production|custom] [--env-file .env] [--set KEY=VALUE ...]
Examples:
  $0 --env development
  $0 --env production --set N8N_BASE_URL=https://n8n.example.com --set OPENAI_API_KEY=sk-...
  $0 --env custom --env-file .env.staging --set APP_ENV=staging
USAGE
}

ENV_CHOICE="development"
ENV_FILE=".env"
OVERRIDES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) ENV_CHOICE="${2:-development}"; shift 2;;
    --env-file) ENV_FILE="${2:-.env}"; shift 2;;
    --set) OVERRIDES+=("${2:-}"); shift 2;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

case "$ENV_CHOICE" in
  development) SRC_FILE=".env.development.example";;
  production)  SRC_FILE=".env.production.example";;
  custom)      SRC_FILE=".env.example";;
  *) err "Invalid --env: $ENV_CHOICE"; exit 1;;
esac

if [[ ! -f "$SRC_FILE" ]]; then
  err "Source env template not found: $SRC_FILE"; exit 2
fi

cp "$SRC_FILE" "$ENV_FILE"
info "Copied $SRC_FILE -> $ENV_FILE"

# Apply overrides
for kv in "${OVERRIDES[@]:-}"; do
  key="${kv%%=*}"; val="${kv#*=}"
  if grep -qE "^${key}=" "$ENV_FILE"; then
    sed -i.bak "s|^${key}=.*$|${key}=${val}|" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
  info "Set ${key} (override)"
done

# Validate
bash enhanced-ai-agent-os/scripts/validate-environment.sh --env-file "$ENV_FILE" || {
  err "Validation failed for $ENV_FILE"; exit 3; }

info "Environment configured and validated: $ENV_FILE"
