#!/usr/bin/env bash
set -euo pipefail

# AI capability smoke tests: validate config and optionally perform a minimal provider request
# Skips external calls if keys are not present.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

need() { command -v "$1" >/dev/null 2>&1 || { err "$1 not found"; exit 2; }; }
need bash

ENV_FILE="${ENV_FILE:-.env}"
if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a || true
else
  warn "ENV_FILE not found: $ENV_FILE (continuing with current env)"
fi

# 1) Run validator
if [[ -f "enhanced-ai-agent-os/scripts/validate-environment.sh" ]]; then
  bash enhanced-ai-agent-os/scripts/validate-environment.sh --env-file "${ENV_FILE}" || warn "Environment validator reported issues"
fi

# 2) Minimal provider checks
prov="${AI_DEFAULT_PROVIDER:-openai}"
case "$prov" in
  openai)
    if [[ -n "${OPENAI_API_KEY:-}" ]] && command -v curl >/dev/null 2>&1; then
      info "OpenAI key present; attempting model list (timeout 5s)"
      # New API style may vary; keep tolerant and do not fail suite on 401/403
      curl -fsS --max-time 5 https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" -H 'Accept: application/json' >/dev/null || warn "OpenAI request failed (ignored)"
    else
      warn "OpenAI key missing or curl not available; skipping external call"
    fi
    ;;
  anthropic)
    if [[ -n "${ANTHROPIC_API_KEY:-}" ]] && command -v curl >/dev/null 2>&1; then
      info "Anthropic key present; attempting models list (timeout 5s)"
      curl -fsS --max-time 5 https://api.anthropic.com/v1/models -H "x-api-key: $ANTHROPIC_API_KEY" -H 'anthropic-version: 2023-06-01' -H 'Accept: application/json' >/dev/null || warn "Anthropic request failed (ignored)"
    else
      warn "Anthropic key missing or curl not available; skipping external call"
    fi
    ;;
  google)
    warn "Google Vertex AI direct HTTP test skipped (requires project/region)."
    ;;
  azure)
    if [[ -n "${AZURE_OPENAI_ENDPOINT:-}" ]] && [[ -n "${AZURE_OPENAI_API_KEY:-}" ]] && command -v curl >/dev/null 2>&1; then
      info "Azure OpenAI present; attempting deployments list (timeout 5s)"
      curl -fsS --max-time 5 "${AZURE_OPENAI_ENDPOINT%/}/openai/deployments?api-version=2024-02-15-preview" -H "api-key: $AZURE_OPENAI_API_KEY" -H 'Accept: application/json' >/dev/null || warn "Azure request failed (ignored)"
    else
      warn "Azure endpoint/key missing or curl not available; skipping external call"
    fi
    ;;
  *)
    warn "Unknown AI_DEFAULT_PROVIDER=$prov; skipping external calls"
    ;;
esac

info "AI capability smoke tests completed"
