#!/usr/bin/env bash
set -euo pipefail

# analyze-metrics.sh
# Runs a set of PromQL queries against Prometheus to derive operational intelligence
# Requires: curl, jq

PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
WINDOW="${WINDOW:-5m}"

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

need(){ command -v "$1" >/dev/null 2>&1 || { err "$1 not found"; exit 2; }; }
need curl; need jq

q(){
  local query="$1"
  curl -fsS --get "$PROMETHEUS_URL/api/v1/query" --data-urlencode "query=$query" | jq -r '.data.result[]? | [(.metric.agent // .metric.workflow_name // .metric.instance // ""), .value[1]] | @tsv'
}

info "Top agents by request rate"
q "topk(5, sum by(agent)(rate(ai_agent_request_total[$WINDOW])))"

info "Agents p95 latency (s)"
q "histogram_quantile(0.95, sum by (le,agent) (rate(ai_agent_latency_seconds_bucket[$WINDOW])))"

info "Model error rate by provider"
q "sum by(provider)(rate(ai_model_error_total[$WINDOW]))"

info "Workflow success rate"
q "sum(rate(workflow_execution_total{status=\"success\"}[$WINDOW])) / sum(rate(workflow_execution_total[$WINDOW]))"

info "Node errors (top 5)"
q "topk(5, sum by(workflow_id,node_type)(rate(workflow_node_error_total[$WINDOW])))"

info "Knowledge graph growth (24h)"
q "increase(kg_nodes_total[24h])"
q "increase(kg_edges_total[24h])"

info "Capacity utilization (CPU, memory)"
q "avg(system_capacity_cpu_utilization)"
q "avg(system_capacity_memory_utilization)"
