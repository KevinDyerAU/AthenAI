#!/usr/bin/env bash
set -euo pipefail

# security-scan.sh
# Runs security assessments: dependency audit, Docker image scan, secret scan, config validation.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

usage() {
  cat <<USAGE
Usage: $0 [--npm-audit] [--docker-image <name[:tag]>] [--trufflehog <path>] [--env-file .env]

Examples:
  $0 --npm-audit --env-file .env
  $0 --docker-image n8nio/n8n:latest
  $0 --trufflehog .

Requires (optional): npm, docker, trivy, trufflehog
USAGE
}

DO_NPM=false
IMG=""
TH_PATH=""
ENV_FILE=".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --npm-audit) DO_NPM=true; shift;;
    --docker-image) IMG="${2:-}"; shift 2;;
    --trufflehog) TH_PATH="${2:-}"; shift 2;;
    --env-file) ENV_FILE="${2:-.env}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

# 1) Env validation
if [[ -f "$ENV_FILE" ]]; then
  info "Validating env: $ENV_FILE"
  bash enhanced-ai-agent-os/scripts/validate-environment.sh --env-file "$ENV_FILE" || warn "Env validation reported issues"
else
  warn "Env file not found: $ENV_FILE"
fi

# 2) npm audit
if [[ "$DO_NPM" == true ]]; then
  if command -v npm >/dev/null 2>&1; then
    info "Running npm audit (production)"
    npm audit --production || warn "npm audit reported vulnerabilities"
  else
    warn "npm not found; skipping npm audit"
  fi
fi

# 3) Docker image scan (Trivy)
if [[ -n "$IMG" ]]; then
  if command -v trivy >/dev/null 2>&1; then
    info "Scanning Docker image with Trivy: $IMG"
    trivy image --severity HIGH,CRITICAL --ignore-unfixed "$IMG" || warn "Trivy reported vulnerabilities"
  else
    warn "trivy not found; skipping image scan"
  fi
fi

# 4) Secret scan (TruffleHog)
if [[ -n "$TH_PATH" ]]; then
  if command -v trufflehog >/dev/null 2>&1; then
    info "Running TruffleHog on $TH_PATH"
    trufflehog filesystem "$TH_PATH" || warn "TruffleHog reported findings"
  else
    warn "trufflehog not found; skipping secret scan"
  fi
fi

info "Security scan completed. Review warnings above."
