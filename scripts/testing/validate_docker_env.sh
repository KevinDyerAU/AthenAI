#!/usr/bin/env bash
set -euo pipefail

ok=0; fail=0

check() {
  local name="$1" cmd="$2"
  echo "Checking: $name"
  if bash -c "$cmd" >/dev/null 2>&1; then
    echo "OK: $name"; ok=$((ok+1))
  else
    echo "FAIL: $name"; fail=$((fail+1))
  fi
}

check "API /system/health" "curl -fsS http://localhost:5000/system/health"
check "Postgres SELECT 1" "docker exec enhanced-ai-postgres psql -U \"${POSTGRES_USER:-postgres}\" -d \"${POSTGRES_DB:-postgres}\" -c 'select 1;'"
check "Neo4j RETURN 1" "docker exec enhanced-ai-neo4j cypher-shell -u \"${NEO4J_USER:-neo4j}\" -p \"${NEO4J_PASSWORD:-neo4j}\" 'RETURN 1;'"
check "Redis PING" "docker exec enhanced-ai-redis redis-cli PING | grep -q PONG"
check "RabbitMQ mgmt health" "curl -fsS -u \"${RABBITMQ_DEFAULT_USER:-guest}:${RABBITMQ_DEFAULT_PASS:-guest}\" http://localhost:15672/api/overview"
check "n8n HTTP root" "curl -fsS http://localhost:5678"

echo "Summary: passed=${ok} failed=${fail}"
if (( fail > 0 )); then
  exit 1
fi
