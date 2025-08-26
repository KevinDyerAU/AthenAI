# Deployment and Operations Guide

## Overview
This guide covers infrastructure requirements, installation, configuration, validation, monitoring, maintenance, troubleshooting, and rollback for NeoV3.

## Prerequisites
- Kubernetes cluster and `kubectl` access.
- Terraform CLI for optional cluster provisioning.
- Container registry access for images (e.g., GHCR).
- Secrets: kubeconfig (base64 for CI), app secrets via K8s secrets.

## Infrastructure
- Terraform modules:
  - EKS: `infrastructure/terraform/eks/`
  - AKS: `infrastructure/terraform/aks/`
  - GKE: `infrastructure/terraform/gke/`
- In-cluster resources: `infrastructure/terraform/k8s/`

### Provision a cluster (example: EKS)
```
cd infrastructure/terraform/eks
terraform init
terraform apply -auto-approve
# Configure kubeconfig:
aws eks update-kubeconfig --name <cluster> --region <region>
```

## Deployment
- Kustomize base and overlays:
  - Base: `infrastructure/k8s/base/`
  - Dev:  `infrastructure/k8s/overlays/dev/`
  - Prod: `infrastructure/k8s/overlays/prod/`
- Parameterized images in base and overlays. CI can override via `kustomize edit set image`.

### Manual deploy
```
# Dev
kubectl apply -k infrastructure/k8s/overlays/dev
kubectl -n neov3-dev rollout status deploy/api-service

# Prod
kubectl apply -k infrastructure/k8s/overlays/prod
kubectl -n neov3 rollout status deploy/api-service
```

### CI/CD deploy (GitHub Actions)
- Workflow: `.github/workflows/deploy.yml`
- Inputs: environment (dev/prod), namespace, api_image, api_tag, push_image, approve_rollback (prod only)
- Prod requires GitHub Environment `prod` approval. No auto-rollback; use `approve_rollback=true` to trigger rollback job.

## Configuration
- K8s ConfigMap: `infrastructure/k8s/base/configmap.yaml`
- Environment examples: `.env*.example`
- Security/sandbox settings in security overrides and K8s securityContext.

## Validation
- Script: `scripts/deploy/validate.sh`
- Verifies namespace, deployment availability, service, HPA, then port-forwards and checks:
  - `/health` endpoint
  - Basic perf probe (20 requests, avg latency)
  - `/metrics` sample

## Monitoring & Observability
- Prometheus Operator integration: `infrastructure/k8s/addons/monitoring/`
- ServiceMonitor for api-service.
- Grafana dashboards (extend under `infrastructure/monitoring/grafana/`).

## Runbooks
- Deployment rollout:
  1) `kubectl apply -k <overlay>`
  2) `kubectl -n <ns> rollout status deploy/api-service`
  3) `bash scripts/deploy/validate.sh <ns> api-service 18080`
- Rollback (manual):
  - `kubectl -n <ns> rollout undo deploy/api-service`
- Scaling:
  - Update HPA: `infrastructure/k8s/base/hpa.yaml` or overlay patches.
- Config changes:
  - Edit ConfigMap and apply, trigger restart if necessary: `kubectl -n <ns> rollout restart deploy/api-service`
- Incident response:
  - Collect diagnostics: `kubectl -n <ns> get all`, `describe`, `logs`.
  - Check health endpoints and metrics.

## Troubleshooting
- Pods CrashLoopBackOff: `kubectl -n <ns> logs deploy/api-service -p`
- Readiness probe failing: check `/health` locally via port-forward.
- Image pull errors: verify registry auth and tags.
- RBAC/ABAC denials: review `infrastructure/security/rbac/policies.yaml` and `api/security/policy.py`.

## Optimization
- Tune HPA targets (CPU/memory) in `hpa.yaml`.
- Resource requests/limits in `api-deployment.yaml` and agent deployments.

## Security
- Apply least-privilege RBAC and sandbox contexts.
- Manage secrets with K8s Secrets/External secrets manager.

## Appendices
- Reference planning docs under `documentation/planning/SMAI/` for architectural rationale.
