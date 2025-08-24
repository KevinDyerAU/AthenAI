#!/usr/bin/env bash
set -euo pipefail

# Validates that the environment validator script runs and detects obvious issues

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

SCRIPT="enhanced-ai-agent-os/scripts/validate-environment.sh"
[[ -f "$SCRIPT" ]] || { err "Validator not found: $SCRIPT"; exit 2; }

# 1) Should pass on example (lenient) template
if [[ -f ".env.example" ]]; then
  info "Checking validator on .env.example"
  bash "$SCRIPT" --env-file .env.example || true # examples may be missing secrets, do not fail hard
fi

# 2) Should fail if required keys missing for selected provider
TMP=$(mktemp)
cat > "$TMP" <<ENV
APP_ENV=development
AI_DEFAULT_PROVIDER=openai
OPENAI_API_KEY=
ENV

set +e
bash "$SCRIPT" --env-file "$TMP"
rc=$?
set -e
if [[ $rc -eq 0 ]]; then
  err "Validator unexpectedly passed with missing OPENAI_API_KEY"
  exit 3
else
  info "Validator correctly failed with rc=$rc for missing OPENAI_API_KEY"
fi

info "Env validator unit test completed"
