#!/usr/bin/env bash
set -euo pipefail

# collect-ai-metrics.sh
# Emits AI and workflow metrics in Prometheus textfile format.
# Intended for node_exporter --collector.textfile and/or Pushgateway.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

# Where to write textfile metrics; ensure node_exporter is configured to scrape this dir
TEXTFILE_DIR="${TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"
OUT_FILE="${OUT_FILE:-ai_metrics.prom}"
AGENT="${AGENT:-generic}"
ENDPOINT="${ENDPOINT:-unknown}"
MODEL_PROVIDER="${MODEL_PROVIDER:-openai}"
MODEL_NAME="${MODEL_NAME:-gpt-4o}" 
QUALITY_EVAL="${QUALITY_EVAL:-auto}"
PUSHGATEWAY="${PUSHGATEWAY:-http://pushgateway:9091}"

usage(){
  cat <<USAGE
Usage: $0 [--textfile-dir DIR] [--out FILE] [--agent NAME] [--endpoint PATH] \
         [--provider PROVIDER] [--model MODEL] [--quality-eval NAME] \
         [--latency SEC] [--tokens-prompt N] [--tokens-completion N] [--cost-usd F] [--status success|error]

Examples:
  $0 --agent planning --endpoint /webhook/planning-agent --latency 0.45 --tokens-prompt 300 --tokens-completion 120 --cost-usd 0.01 --status success
  TEXTFILE_DIR=./out $0 ...
USAGE
}

LATENCY=""
TOK_PROMPT=0
TOK_COMPLETION=0
COST_USD=""
STATUS="success"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --textfile-dir) TEXTFILE_DIR="$2"; shift 2;;
    --out) OUT_FILE="$2"; shift 2;;
    --agent) AGENT="$2"; shift 2;;
    --endpoint) ENDPOINT="$2"; shift 2;;
    --provider) MODEL_PROVIDER="$2"; shift 2;;
    --model) MODEL_NAME="$2"; shift 2;;
    --quality-eval) QUALITY_EVAL="$2"; shift 2;;
    --latency) LATENCY="$2"; shift 2;;
    --tokens-prompt) TOK_PROMPT="$2"; shift 2;;
    --tokens-completion) TOK_COMPLETION="$2"; shift 2;;
    --cost-usd) COST_USD="$2"; shift 2;;
    --status) STATUS="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

mkdir -p "$TEXTFILE_DIR"
TMP="$(mktemp)"

# Required metric family names match infrastructure/monitoring/custom-metrics/ai_metrics.yaml
{
  echo "# TYPE ai_agent_request_total counter"
  echo "ai_agent_request_total{agent=\"$AGENT\",endpoint=\"$ENDPOINT\",status=\"$STATUS\"} 1"

  if [[ -n "$LATENCY" ]]; then
    echo "# TYPE ai_agent_latency_seconds summary"
    echo "ai_agent_latency_seconds_sum{agent=\"$AGENT\",endpoint=\"$ENDPOINT\"} $LATENCY"
    echo "ai_agent_latency_seconds_count{agent=\"$AGENT\",endpoint=\"$ENDPOINT\"} 1"
  fi

  echo "# TYPE ai_model_tokens_total counter"
  if (( TOK_PROMPT > 0 )); then
    echo "ai_model_tokens_total{agent=\"$AGENT\",model=\"$MODEL_NAME\",provider=\"$MODEL_PROVIDER\",token_type=\"prompt\"} $TOK_PROMPT"
  fi
  if (( TOK_COMPLETION > 0 )); then
    echo "ai_model_tokens_total{agent=\"$AGENT\",model=\"$MODEL_NAME\",provider=\"$MODEL_PROVIDER\",token_type=\"completion\"} $TOK_COMPLETION"
    echo "ai_model_tokens_total{agent=\"$AGENT\",model=\"$MODEL_NAME\",provider=\"$MODEL_PROVIDER\",token_type=\"total\"} $(( TOK_PROMPT + TOK_COMPLETION ))"
  fi

  if [[ -n "$COST_USD" ]]; then
    echo "# TYPE ai_model_cost_usd_total counter"
    echo "ai_model_cost_usd_total{agent=\"$AGENT\",model=\"$MODEL_NAME\",provider=\"$MODEL_PROVIDER\"} $COST_USD"
  fi

  echo "# TYPE ai_response_quality_score gauge"
  echo "ai_response_quality_score{agent=\"$AGENT\",evaluation=\"$QUALITY_EVAL\"} 0"
} > "$TMP"

# Write to textfile dir
mv "$TMP" "$TEXTFILE_DIR/$OUT_FILE"
info "Wrote metrics to $TEXTFILE_DIR/$OUT_FILE"

# Optional push to Pushgateway if provided
if [[ -n "$PUSHGATEWAY" ]]; then
  if command -v curl >/dev/null 2>&1; then
    info "Pushing to Pushgateway $PUSHGATEWAY"
    curl -fsS --data-binary @"$TEXTFILE_DIR/$OUT_FILE" "$PUSHGATEWAY/metrics/job/ai_agent/instance/$(hostname)" || warn "Pushgateway push failed"
  else
    warn "curl not found; cannot push to Pushgateway"
  fi
fi
