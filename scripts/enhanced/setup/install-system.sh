#!/usr/bin/env bash
set -euo pipefail

# install-system.sh
# Installs/bootstraps Enhanced AI Agent OS using Docker (recommended) or local runtime.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

usage() {
  cat <<USAGE
Usage: $0 [--mode docker|local] [--env-file .env] [--no-start]

Modes:
  docker  Use Docker/Docker Compose (recommended)
  local   Prepare local host dependencies (Node, n8n) – best for development

Examples:
  $0 --mode docker --env-file .env
  $0 --mode local  --env-file .env --no-start
USAGE
}

MODE="docker"
ENV_FILE=".env"
NO_START=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:-docker}"; shift 2;;
    --env-file) ENV_FILE="${2:-.env}"; shift 2;;
    --no-start) NO_START=true; shift;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ ! -f "$ENV_FILE" ]]; then
  err "Env file not found: $ENV_FILE"
  exit 2
fi

# Load minimal vars for compose
set -a; source "$ENV_FILE"; set +a || true

if [[ "$MODE" == "docker" ]]; then
  info "Checking Docker..."
  if ! command -v docker >/dev/null 2>&1; then err "Docker not found. Install Docker Desktop or Engine."; exit 3; fi
  if ! command -v docker compose >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
    err "Docker Compose v2 not found. Update Docker Desktop or install compose plugin."; exit 3
  fi
  info "Generating minimal docker-compose.yml (if missing)"
  cat > docker-compose.yml <<'YAML'
version: "3.9"
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "${PORT:-5678}:5678"
    environment:
      - N8N_PORT=5678
      - N8N_HOST=0.0.0.0
      - N8N_PROTOCOL=http
      - N8N_BASE_URL=${N8N_BASE_URL}
    env_file:
      - ${ENV_FILE:-.env}
    volumes:
      - ./data/n8n:/home/node/.n8n
    restart: unless-stopped
YAML
  info "Docker Compose file ready."
  if [[ "$NO_START" == false ]]; then
    info "Starting stack..."
    if command -v docker compose >/dev/null 2>&1; then docker compose up -d; else docker-compose up -d; fi
    info "Stack started. Visit: ${N8N_BASE_URL:-http://localhost:5678}"
  else
    info "NO_START set. Skipping stack start."
  fi
elif [[ "$MODE" == "local" ]]; then
  info "Preparing local runtime..."
  if ! command -v node >/dev/null 2>&1; then warn "Node.js not found. Install LTS from https://nodejs.org/"; fi
  if ! command -v npx >/dev/null 2>&1; then warn "npx not found. Ensure Node.js includes npm."; fi
  info "You can run n8n locally via: npx n8n start --tunnel"
else
  err "Unknown mode: $MODE"; exit 1
fi

info "Running environment validation..."
bash enhanced-ai-agent-os/scripts/validate-environment.sh --env-file "$ENV_FILE" || {
  err "Environment validation failed."; exit 4;
}

info "Installation completed."
