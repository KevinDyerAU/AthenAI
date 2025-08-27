#!/usr/bin/env bash
set -euo pipefail

ok=0; fail=0

get_env_from_container() {
  local cname="$1" key="$2"
  docker exec "$cname" /bin/sh -c "printenv $key" 2>/dev/null || true
}

check() {
  local name="$1" cmd="$2"
  echo "Checking: $name"
  if bash -c "$cmd" >/dev/null 2>&1; then
    echo "OK: $name"; ok=$((ok+1))
  else
    echo "FAIL: $name"; fail=$((fail+1))
  fi
}

API_PORT="${API_HOST_PORT:-8000}"

PG_USER="$(get_env_from_container enhanced-ai-postgres POSTGRES_USER)"
PG_DB="$(get_env_from_container enhanced-ai-postgres POSTGRES_DB)"
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-postgres}"

RMQ_USER="$(get_env_from_container enhanced-ai-rabbitmq RABBITMQ_DEFAULT_USER)"
RMQ_PASS="$(get_env_from_container enhanced-ai-rabbitmq RABBITMQ_DEFAULT_PASS)"
RMQ_USER="${RMQ_USER:-guest}"
RMQ_PASS="${RMQ_PASS:-guest}"

NEO4J_USER="neo4j"
NEO4J_PASS="$(docker exec enhanced-ai-neo4j /bin/sh -lc 'echo \"$NEO4J_AUTH\" | awk -F\"/\" \"{print \\$2}\"' 2>/dev/null || true)"
NEO4J_PASS="${NEO4J_PASS:-neo4j}"

check "API /system/health" "curl -fsS http://localhost:${API_PORT}/system/health"
check "Postgres SELECT 1" "docker exec enhanced-ai-postgres psql -U \"${PG_USER}\" -d \"${PG_DB}\" -c 'select 1;'"
check "Neo4j RETURN 1" "docker exec enhanced-ai-neo4j cypher-shell -u \"${NEO4J_USER}\" -p \"${NEO4J_PASS}\" 'RETURN 1;'"
check "Redis PING" "docker exec enhanced-ai-redis redis-cli PING | grep -q PONG"
check "RabbitMQ mgmt health" "curl -fsS -u \"${RMQ_USER}:${RMQ_PASS}\" http://localhost:15672/api/overview"
check "n8n HTTP root" "curl -fsS http://localhost:5678"

echo \"Summary: passed=${ok} failed=${fail}\"
if (( fail > 0 )); then
  exit 1
fi
