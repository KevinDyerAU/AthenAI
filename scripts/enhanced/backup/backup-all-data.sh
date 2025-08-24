#!/usr/bin/env bash
set -euo pipefail

# backup-all-data.sh
# Creates backups for Postgres, Neo4j, and n8n application data directory.
# Optional upload to S3 if AWS_* vars and S3_BUCKET are set.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

usage() {
  cat <<USAGE
Usage: $0 [--output-dir ./backups] [--include {postgres,neo4j,n8n,all}] [--s3]

Examples:
  $0 --output-dir ./backups --include all
  $0 --include postgres --s3

Environment:
  DB_* for Postgres (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
  NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
  N8N_DATA_DIR (default: ./data/n8n)
  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET (for --s3)
USAGE
}

OUT_DIR="./backups"
INCLUDE="all"
DO_S3=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir) OUT_DIR="${2:-./backups}"; shift 2;;
    --include) INCLUDE="${2:-all}"; shift 2;;
    --s3) DO_S3=true; shift;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

mkdir -p "$OUT_DIR"
STAMP=$(date -u +"%Y%m%dT%H%M%SZ")

backup_postgres() {
  local f="$OUT_DIR/postgres_${DB_NAME:-db}_$STAMP.sql.gz"
  if ! command -v pg_dump >/dev/null 2>&1; then warn "pg_dump not found; skipping Postgres backup"; return; fi
  : "${DB_HOST:?DB_HOST required}" "${DB_PORT:?DB_PORT required}" "${DB_USER:?DB_USER required}" "${DB_NAME:?DB_NAME required}"
  info "Backing up Postgres database $DB_NAME -> $f"
  PGPASSWORD="${DB_PASSWORD:-}" pg_dump -h "$DB_HOST" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" | gzip -9 > "$f"
}

backup_neo4j() {
  local fdir="$OUT_DIR/neo4j_$STAMP"
  if ! command -v neo4j-admin >/dev/null 2>&1; then warn "neo4j-admin not found; attempting cypher-shell dump"; fi
  if command -v neo4j-admin >/dev/null 2>&1; then
    mkdir -p "$fdir"
    info "Exporting Neo4j database to $fdir (requires local Neo4j access)"
    neo4j-admin database dump neo4j --to-path="$fdir" || warn "neo4j-admin dump failed"
  elif command -v cypher-shell >/dev/null 2>&1; then
    local f="$OUT_DIR/neo4j_$STAMP.cypher.gz"
    info "Exporting Neo4j via cypher-shell -> $f"
    echo "CALL apoc.export.cypher.all(null,{useOptimizations:true, format:'cypher-shell'})" \
      | cypher-shell -a "${NEO4J_URI:-bolt://localhost:7687}" -u "${NEO4J_USER:-neo4j}" -p "${NEO4J_PASSWORD:-}" \
      | gzip -9 > "$f" || warn "cypher export failed (ensure APOC permissions)"
  else
    warn "Neo4j CLI not found; skipping Neo4j backup"
  fi
}

backup_n8n() {
  local data_dir="${N8N_DATA_DIR:-./data/n8n}"
  local f="$OUT_DIR/n8n_data_$STAMP.tar.gz"
  if [[ -d "$data_dir" ]]; then
    info "Archiving n8n data dir $data_dir -> $f"
    tar -C "$(dirname "$data_dir")" -czf "$f" "$(basename "$data_dir")"
  else
    warn "n8n data dir not found: $data_dir"
  fi
}

upload_s3() {
  if [[ "$DO_S3" != true ]]; then return; fi
  : "${AWS_ACCESS_KEY_ID:?AWS_ACCESS_KEY_ID required for --s3}" "${AWS_SECRET_ACCESS_KEY:?AWS_SECRET_ACCESS_KEY required for --s3}" "${AWS_REGION:?AWS_REGION required for --s3}" "${S3_BUCKET:?S3_BUCKET required for --s3}"
  if ! command -v aws >/dev/null 2>&1; then err "aws CLI not found"; return 1; fi
  info "Uploading backups to s3://${S3_BUCKET}/"
  aws s3 cp "$OUT_DIR" "s3://${S3_BUCKET}/" --recursive --region "$AWS_REGION"
}

case "$INCLUDE" in
  all) backup_postgres || true; backup_neo4j || true; backup_n8n || true;;
  postgres) backup_postgres || true;;
  neo4j) backup_neo4j || true;;
  n8n) backup_n8n || true;;
  *) err "Unknown include: $INCLUDE"; exit 1;;
esac

upload_s3 || true
info "Backup completed. Artifacts in $OUT_DIR"
