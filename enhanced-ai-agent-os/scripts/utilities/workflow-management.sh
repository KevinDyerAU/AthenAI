#!/usr/bin/env bash
set -euo pipefail

# workflow-management.sh
# Manage n8n workflows via REST API: list, export, import, activate, deactivate.
# Requires N8N API credentials (Personal Access Token or basic auth).

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

usage() {
  cat <<USAGE
Usage: $0 --api-url <url> (--api-key <token> | --basic "user:pass") <command> [args]

Commands:
  list                                     List workflows (id, name, active)
  export   --out-dir <dir> [--filter <re>] Export all (or filtered by name regex) to JSON files
  import   --in-dir <dir> [--activate]     Import all JSON files from directory
  activate   --id <id>                     Activate workflow by id
  deactivate --id <id>                     Deactivate workflow by id

Examples:
  $0 --api-url http://localhost:5678 --api-key XXXXX list
  $0 --api-url http://localhost:5678 --api-key XXXXX export --out-dir ./wf
  $0 --api-url http://localhost:5678 --api-key XXXXX import --in-dir ./wf --activate

Auth:
  Create a Personal Access Token in n8n and pass via --api-key. Alternatively, use --basic 'user:password'.
USAGE
}

API_URL=""
API_KEY=""
BASIC_AUTH=""
CMD=""

OUT_DIR=""
IN_DIR=""
FILTER_RE=""
WF_ID=""
DO_ACTIVATE=false

need() { command -v "$1" >/dev/null 2>&1 || { err "$1 not found"; exit 1; }; }
need curl

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-url) API_URL="${2:-}"; shift 2;;
    --api-key) API_KEY="${2:-}"; shift 2;;
    --basic)   BASIC_AUTH="${2:-}"; shift 2;;
    list|export|import|activate|deactivate) CMD="$1"; shift;;
    --out-dir) OUT_DIR="${2:-}"; shift 2;;
    --in-dir)  IN_DIR="${2:-}"; shift 2;;
    --filter)  FILTER_RE="${2:-}"; shift 2;;
    --id)      WF_ID="${2:-}"; shift 2;;
    --activate) DO_ACTIVATE=true; shift;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

[[ -n "$API_URL" ]] || { err "--api-url is required"; exit 1; }
if [[ -z "$API_KEY" && -z "$BASIC_AUTH" ]]; then err "Provide --api-key or --basic"; exit 1; fi

AUTH_HEADER=()
if [[ -n "$API_KEY" ]]; then
  AUTH_HEADER=(-H "X-N8N-API-KEY: $API_KEY")
else
  AUTH_HEADER=(-u "$BASIC_AUTH")
fi

api() {
  local method="$1" path="$2"; shift 2
  curl -fsS -X "$method" "${API_URL%/}${path}" "${AUTH_HEADER[@]}" -H 'Content-Type: application/json' "$@"
}

case "$CMD" in
  list)
    info "Listing workflows"
    api GET "/rest/workflows" | jq -r '.data[] | "\(.id)\t\(.name)\tactive=\(.active)"' || true
    ;;
  export)
    [[ -n "$OUT_DIR" ]] || { err "--out-dir required"; exit 1; }
    mkdir -p "$OUT_DIR"
    info "Fetching workflows..."
    data=$(api GET "/rest/workflows") || { err "Failed to fetch workflows"; exit 2; }
    echo "$data" | jq -c '.data[]' | while read -r row; do
      name=$(echo "$row" | jq -r '.name')
      id=$(echo "$row" | jq -r '.id')
      if [[ -n "$FILTER_RE" && ! "$name" =~ $FILTER_RE ]]; then continue; fi
      info "Exporting [$id] $name"
      api GET "/rest/workflows/$id" | jq '.' > "$OUT_DIR/${id}_$(echo "$name" | tr ' /' '__').json"
    done
    ;;
  import)
    [[ -d "$IN_DIR" ]] || { err "--in-dir directory required"; exit 1; }
    shopt -s nullglob
    for f in "$IN_DIR"/*.json; do
      info "Importing $f"
      body=$(jq '{name:.name, nodes:.nodes, connections:.connections, settings:(.settings//{}), staticData:(.staticData//{})}' "$f")
      created=$(api POST "/rest/workflows" --data "$body") || { warn "Failed to import $f"; continue; }
      new_id=$(echo "$created" | jq -r '.id')
      info "Created workflow id=$new_id"
      if [[ "$DO_ACTIVATE" == true ]]; then
        info "Activating $new_id"
        api POST "/rest/workflows/$new_id/activate" --data '{"activate":true}' >/dev/null || warn "Activation failed for $new_id"
      fi
    done
    ;;
  activate)
    [[ -n "$WF_ID" ]] || { err "--id required"; exit 1; }
    api POST "/rest/workflows/$WF_ID/activate" --data '{"activate":true}' >/dev/null && info "Activated $WF_ID"
    ;;
  deactivate)
    [[ -n "$WF_ID" ]] || { err "--id required"; exit 1; }
    api POST "/rest/workflows/$WF_ID/activate" --data '{"activate":false}' >/dev/null && info "Deactivated $WF_ID"
    ;;
  *) usage; exit 1;;
esac
