#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
ENV_FILE="${ROOT_DIR}/.env"
SCHEMA_FILE="${ROOT_DIR}/db/neo4j/schema.cypher"
CONTAINER="enhanced-ai-neo4j"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env not found at $ENV_FILE" >&2
  exit 1
fi
if [[ ! -f "$SCHEMA_FILE" ]]; then
  echo "ERROR: schema.cypher not found at $SCHEMA_FILE" >&2
  exit 1
fi

# shellcheck disable=SC2046
export $(grep -E '^(NEO4J_PASSWORD)=' "$ENV_FILE" | xargs -d '\n')

if [[ -z "${NEO4J_PASSWORD:-}" ]]; then
  echo "ERROR: NEO4J_PASSWORD not set in .env" >&2
  exit 1
fi

echo "Applying Neo4j schema to $CONTAINER"
# Use cypher-shell inside the container
cat "$SCHEMA_FILE" | docker exec -i "$CONTAINER" cypher-shell -a neo4j:7687 -u neo4j -p "$NEO4J_PASSWORD"

echo "Neo4j schema applied successfully."
