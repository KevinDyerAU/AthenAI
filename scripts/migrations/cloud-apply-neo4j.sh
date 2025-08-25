#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
ENV_FILE_ROOT="${ROOT_DIR}/.env.cloud"
SCHEMA_FILE="${ROOT_DIR}/db/neo4j/schema.cypher"

if [[ ! -f "$SCHEMA_FILE" ]]; then
  echo "ERROR: schema.cypher not found at $SCHEMA_FILE" >&2
  exit 1
fi

# Load .env.cloud if present
if [[ -f "$ENV_FILE_ROOT" ]]; then
  # shellcheck disable=SC2046
  export $(grep -E '^(NEO4J_URI|NEO4J_USERNAME|NEO4J_PASSWORD)=' "$ENV_FILE_ROOT" | xargs -d '\n' || true)
else
  echo "WARN: .env.cloud not found at $ENV_FILE_ROOT; relying on environment only" >&2
fi

NEO4J_URI=${NEO4J_URI:-}
NEO4J_USERNAME=${NEO4J_USERNAME:-neo4j}
NEO4J_PASSWORD=${NEO4J_PASSWORD:-}

if [[ -z "$NEO4J_URI" || -z "$NEO4J_PASSWORD" ]]; then
  echo "ERROR: NEO4J_URI and NEO4J_PASSWORD are required. Set them in .env.cloud or environment." >&2
  exit 1
fi

# Ensure cypher-shell exists (Neo4j client). If not, try dockerized fallback.
if command -v cypher-shell >/dev/null 2>&1; then
  echo "Applying Neo4j schema via cypher-shell to $NEO4J_URI as $NEO4J_USERNAME"
  cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" --file "$SCHEMA_FILE"
else
  echo "cypher-shell not found locally. Attempting dockerized cypher-shell..."
  docker run --rm -i --network host -e NEO4J_URI -e NEO4J_USERNAME -e NEO4J_PASSWORD neo4j:5.20.0 \
    bash -lc 'cat > /tmp/schema.cypher; cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" --file /tmp/schema.cypher' < "$SCHEMA_FILE"
fi

echo "Neo4j cloud schema applied successfully."
