#!/usr/bin/env bash
# Lightweight post-deploy smoke tests
# This script is intended to be invoked by deploy-local.sh and deploy-local.ps1
# It performs quick HTTP and container checks and returns non-zero if any fail.

set -u

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log(){ echo -e "${BLUE}[smoke]${NC} $*"; }
success(){ echo -e "${GREEN}[OK]${NC} $*"; }
warn(){ echo -e "${YELLOW}[WARN]${NC} $*"; }
err(){ echo -e "${RED}[FAIL]${NC} $*"; }

# Helper to read KEY from .env in repo root if present
get_dotenv_value(){
  local key="$1" env_file="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")/.env"
  [[ -f "$env_file" ]] || { echo ""; return; }
  local line
  line=$(grep -E "^[[:space:]]*${key}[[:space:]]*=" "$env_file" | head -n1 || true)
  [[ -z "$line" ]] && { echo ""; return; }
  local val="${line#*=}"; val="${val%$'\r'}"
  if [[ "${val:0:1}" == '"' && "${val: -1}" == '"' ]] || [[ "${val:0:1}" == "'" && "${val: -1}" == "'" ]]; then
    val="${val:1:${#val}-2}"
  fi
  echo "$val"
}

check_http(){
  local label="$1" url="$2"; local code
  code=$(curl -fsS -o /dev/null -w '%{http_code}' "$url" 2>/dev/null || true)
  if [[ "$code" == "200" || "$code" == "204" ]]; then success "$label HTTP ${code}"; return 0; else err "$label HTTP ${code:-no-conn} ($url)"; return 1; fi
}

check_container_running(){
  local name="$1"
  if docker ps --format '{{.Names}}' | grep -qx "$name"; then success "container running: $name"; return 0; else err "container not running: $name"; return 1; fi
}

main(){
  local fails=0
  local api_port="${API_HOST_PORT:-}"
  [[ -z "$api_port" ]] && api_port="$(get_dotenv_value API_HOST_PORT)"
  [[ -z "$api_port" ]] && api_port=5000

  log "Running smoke checks"
  check_http "API /system/health" "http://localhost:${api_port}/system/health" || fails=$((fails+1))
  check_http "Grafana /api/health" "http://localhost:3000/api/health" || fails=$((fails+1))
  check_http "Prometheus /-/ready" "http://localhost:9090/-/ready" || fails=$((fails+1))
  check_http "n8n root" "http://localhost:5678/" || fails=$((fails+1))

  # RabbitMQ management (auth)
  local rmq_user="${RABBITMQ_DEFAULT_USER:-}"
  local rmq_pass="${RABBITMQ_DEFAULT_PASS:-}"
  [[ -z "$rmq_user" ]] && rmq_user="$(get_dotenv_value RABBITMQ_DEFAULT_USER)"
  [[ -z "$rmq_pass" ]] && rmq_pass="$(get_dotenv_value RABBITMQ_DEFAULT_PASS)"
  if [[ -n "$rmq_user" && -n "$rmq_pass" ]]; then
    if curl -fsS "http://localhost:15672/api/overview" -u "$rmq_user:$rmq_pass" >/dev/null 2>&1; then
      success "RabbitMQ management API"
    else
      err "RabbitMQ management API"
      fails=$((fails+1))
    fi
  else
    warn "RabbitMQ credentials not set; skipping management API check"
  fi

  check_container_running enhanced-ai-postgres || fails=$((fails+1))
  check_container_running enhanced-ai-neo4j || fails=$((fails+1))
  check_container_running enhanced-ai-rabbitmq || fails=$((fails+1))
  check_container_running enhanced-ai-agent-api || fails=$((fails+1))

  # DB and cache round-trip checks via docker exec
  local pg_user="${POSTGRES_USER:-}"
  local pg_db="${POSTGRES_DB:-}"
  [[ -z "$pg_user" ]] && pg_user="$(get_dotenv_value POSTGRES_USER)"
  [[ -z "$pg_db" ]] && pg_db="$(get_dotenv_value POSTGRES_DB)"
  [[ -z "$pg_user" ]] && pg_user="postgres"
  [[ -z "$pg_db" ]] && pg_db="postgres"
  if docker exec enhanced-ai-postgres psql -U "$pg_user" -d "$pg_db" -c "select 1;" >/dev/null 2>&1; then
    success "Postgres query select 1"
  else
    err "Postgres query select 1"
    fails=$((fails+1))
  fi

  local neo_user="${NEO4J_USER:-}"
  local neo_pass="${NEO4J_PASSWORD:-}"
  [[ -z "$neo_user" ]] && neo_user="$(get_dotenv_value NEO4J_USER)"
  [[ -z "$neo_pass" ]] && neo_pass="$(get_dotenv_value NEO4J_PASSWORD)"
  [[ -z "$neo_user" ]] && neo_user="neo4j"
  if docker exec enhanced-ai-neo4j cypher-shell -u "$neo_user" -p "$neo_pass" "RETURN 1;" >/dev/null 2>&1; then
    success "Neo4j RETURN 1"
  else
    err "Neo4j RETURN 1"
    fails=$((fails+1))
  fi

  if docker exec enhanced-ai-redis redis-cli PING | grep -q PONG; then
    success "Redis PING"
  else
    err "Redis PING"
    fails=$((fails+1))
  fi

  if [[ $fails -gt 0 ]]; then
    err "Smoke tests failed: $fails check(s) failed"
    exit 1
  else
    success "All smoke tests passed"
    exit 0
  fi
}

main "$@"
