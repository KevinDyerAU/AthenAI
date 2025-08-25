#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
ENV_FILE_ROOT="${ROOT_DIR}/.env.cloud"
SCHEMA_FILE="${ROOT_DIR}/db/postgres/schema.sql"

if [[ ! -f "$SCHEMA_FILE" ]]; then
  echo "ERROR: schema.sql not found at $SCHEMA_FILE" >&2
  exit 1
fi

# Load .env.cloud if present
if [[ -f "$ENV_FILE_ROOT" ]]; then
  # shellcheck disable=SC2046
  export $(grep -E '^(DATABASE_URL|POSTGRES_|PGHOST|PGPORT|PGUSER|PGPASSWORD|PGDATABASE)=' "$ENV_FILE_ROOT" | xargs -d '\n' || true)
else
  echo "WARN: .env.cloud not found at $ENV_FILE_ROOT; relying on environment only" >&2
fi

# Prefer DATABASE_URL if provided
if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "Applying PostgreSQL schema via DATABASE_URL"
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$SCHEMA_FILE"
else
  # Fallback to discrete vars
  PGHOST=${PGHOST:-${POSTGRES_HOST:-localhost}}
  PGPORT=${PGPORT:-${POSTGRES_PORT:-5432}}
  PGUSER=${PGUSER:-${POSTGRES_USER:-postgres}}
  PGPASSWORD=${PGPASSWORD:-${POSTGRES_PASSWORD:-}}
  PGDATABASE=${PGDATABASE:-${POSTGRES_DB:-postgres}}
  export PGPASSWORD
  if [[ -z "$PGPASSWORD" ]]; then
    echo "ERROR: No PGPASSWORD provided; set DATABASE_URL or POSTGRES_PASSWORD/PGPASSWORD in .env.cloud" >&2
    exit 1
  fi
  echo "Applying PostgreSQL schema to $PGHOST:$PGPORT db=$PGDATABASE user=$PGUSER"
  psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=1 -f "$SCHEMA_FILE"
fi

echo "PostgreSQL cloud schema applied successfully."
