#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
ENV_FILE="${ROOT_DIR}/.env"
SCHEMA_FILE="${ROOT_DIR}/db/postgres/schema.sql"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.yml"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env not found at $ENV_FILE" >&2
  exit 1
fi
if [[ ! -f "$SCHEMA_FILE" ]]; then
  echo "ERROR: schema.sql not found at $SCHEMA_FILE" >&2
  exit 1
fi

# shellcheck disable=SC2046
export $(grep -E '^(POSTGRES_USER|POSTGRES_PASSWORD|POSTGRES_DB)=' "$ENV_FILE" | xargs -d '\n')

if [[ -z "${POSTGRES_DB:-}" || -z "${POSTGRES_USER:-}" ]]; then
  echo "ERROR: POSTGRES_DB/POSTGRES_USER not set in .env" >&2
  exit 1
fi

CONTAINER="enhanced-ai-postgres"

echo "Applying PostgreSQL schema to $CONTAINER database=$POSTGRES_DB user=$POSTGRES_USER"
# Pipe file via stdin to avoid copying into container
cat "$SCHEMA_FILE" | docker exec -i "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "Done. Validating indexes..."
QUERY="SELECT relname FROM pg_class WHERE relkind='i' ORDER BY relname LIMIT 5;"
docker exec -i "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "$QUERY"

echo "PostgreSQL schema applied successfully."
