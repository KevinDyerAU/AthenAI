#!/usr/bin/env bash
set -euo pipefail

# log-analysis.sh
# Analyzes and manages logs: filter, summarize, rotate, and cleanup.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

usage() {
  cat <<USAGE
Usage: $0 [--path <file>] [--since '2025-08-20'] [--grep <pattern>] [--top-errors] [--rotate] [--clean-days <N>]

Examples:
  $0 --path ./audit.log --top-errors
  $0 --path ./audit.log --grep ERROR --since '2025-01-01'
  $0 --path ./audit.log --rotate
  $0 --path ./audit.log --clean-days 14

Environment:
  AUDIT_LOG_PATH (default: ./audit.log)
USAGE
}

LOG_PATH="${AUDIT_LOG_PATH:-./audit.log}"
SINCE=""
GREP_PATTERN=""
TOP_ERRORS=false
ROTATE=false
CLEAN_DAYS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path) LOG_PATH="${2:-$LOG_PATH}"; shift 2;;
    --since) SINCE="${2:-}"; shift 2;;
    --grep) GREP_PATTERN="${2:-}"; shift 2;;
    --top-errors) TOP_ERRORS=true; shift;;
    --rotate) ROTATE=true; shift;;
    --clean-days) CLEAN_DAYS="${2:-0}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ ! -f "$LOG_PATH" ]]; then
  err "Log file not found: $LOG_PATH"; exit 2
fi

work_file="$LOG_PATH"

# Filter since date using awk (expects ISO timestamps in lines)
if [[ -n "$SINCE" ]]; then
  info "Filtering since $SINCE"
  work_file=$(mktemp)
  awk -v since="$SINCE" 'BEGIN{FS=" ";} { if ($1 >= since) print $0; }' "$LOG_PATH" > "$work_file" || true
fi

# Grep pattern
if [[ -n "$GREP_PATTERN" ]]; then
  info "Applying grep pattern: $GREP_PATTERN"
  tmp=$(mktemp)
  grep -E "$GREP_PATTERN" "$work_file" > "$tmp" || true
  mv "$tmp" "$work_file"
fi

# Top errors summary
if [[ "$TOP_ERRORS" == true ]]; then
  info "Top error messages:"
  awk '/ERROR|Error|error/ { $1=""; $2=""; sub(/^\s+/, ""); print }' "$work_file" \
    | sed 's/[[:space:]]\+/ /g' \
    | sort | uniq -c | sort -nr | head -20 || true
fi

# Basic stats
info "Log statistics:"
lines=$(wc -l < "$work_file" || echo 0)
errors=$(grep -Ec 'ERROR|Error|error' "$work_file" || echo 0)
warnings=$(grep -Ec 'WARN|Warn|warning' "$work_file" || echo 0)
info "lines=$lines errors=$errors warnings=$warnings"

# Rotate log
if [[ "$ROTATE" == true ]]; then
  ts=$(date -u +"%Y%m%dT%H%M%SZ")
  rotated="${LOG_PATH}.${ts}"
  info "Rotating $LOG_PATH -> $rotated"
  mv "$LOG_PATH" "$rotated"
  : > "$LOG_PATH"
fi

# Cleanup old rotated logs
if [[ "$CLEAN_DAYS" != 0 ]]; then
  dir=$(dirname "$LOG_PATH")
  base=$(basename "$LOG_PATH")
  info "Cleaning rotated logs older than $CLEAN_DAYS days in $dir"
  find "$dir" -type f -name "${base}.*" -mtime +"$CLEAN_DAYS" -print -delete || true
fi

info "Log analysis completed."
