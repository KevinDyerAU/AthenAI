#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT=${1:-dev}
NAMESPACE=${2:-}
OVERLAY_DIR="infrastructure/k8s/overlays/${ENVIRONMENT}"

if [[ ! -d "$OVERLAY_DIR" ]]; then
  echo "Unknown environment: $ENVIRONMENT" >&2
  echo "Available: $(ls infrastructure/k8s/overlays)" >&2
  exit 1
fi

# Build and apply kustomize overlay
kubectl apply -k "$OVERLAY_DIR"

echo "Waiting for api-service rollout..."
# Determine namespace if not provided
if [[ -z "$NAMESPACE" ]]; then
  # Try to parse from kustomization.yaml; fallback to neov3
  NS_LINE=$(grep -E '^namespace:' "$OVERLAY_DIR/kustomization.yaml" | head -n1 | awk '{print $2}') || true
  NS=${NS_LINE:-neov3}
else
  NS="$NAMESPACE"
fi

DEPLOY_NAME=$(kubectl -n "$NS" get deploy -l app=api-service -o jsonpath='{.items[0].metadata.name}')
kubectl -n "$NS" rollout status deploy/"$DEPLOY_NAME" --timeout=180s

echo "Deployment applied for environment: $ENVIRONMENT"
