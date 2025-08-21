#!/usr/bin/env bash
set -euo pipefail
# Simple Postgres DB backup to local file using pg_dump
: "${DATABASE_URL:?Set DATABASE_URL}"
OUT_DIR=${1:-"./backups"}
mkdir -p "$OUT_DIR"
TS=$(date +%Y%m%d-%H%M%S)
FILE="$OUT_DIR/db-backup-$TS.sql"
echo "[backup] Writing $FILE"
pg_dump "$DATABASE_URL" > "$FILE"
echo "[backup] Done"
