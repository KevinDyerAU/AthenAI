# NeoV3 Architecture and Design Documentation

## Overview
NeoV3 is an autonomous agent ecosystem comprising an API service, supporting databases (Postgres, Neo4j), messaging (RabbitMQ), agent services, and observability stack. It targets multi-environment deployments (dev/prod) with IaC and K8s orchestration.

## Components
- API Service (`api/`), exposes REST/WS. K8s manifests in `infrastructure/k8s/base/api-*.yaml`.
- Agent Services: `agent-lifecycle-manager`, `knowledge-drift-detector`, `self-healing-monitor`. K8s manifests in `infrastructure/k8s/base/*deployment.yaml`.
- Datastores: Postgres (pgvector) and Neo4j. Compose for local; external services for K8s.
- Messaging: RabbitMQ for inter-agent communication.
- Observability: Prometheus Operator integration (`infrastructure/k8s/addons/monitoring/`), ServiceMonitor, Grafana dashboards.
- Security: RBAC/ABAC in API (`api/security/policy.py`), sandbox constraints (Docker/K8s security context), secrets via K8s mechanisms.

## Environments and Deployment Model
- Kustomize base: `infrastructure/k8s/base/`
- Overlays: `infrastructure/k8s/overlays/dev/`, `.../prod/`
- Images parameterized in `kustomization.yaml` for CI-driven rollouts.
- Terraform for cluster and k8s resources:
  - EKS: `infrastructure/terraform/eks/`
  - AKS: `infrastructure/terraform/aks/`
  - GKE: `infrastructure/terraform/gke/`
  - K8s resources (namespace/config): `infrastructure/terraform/k8s/`

## Data Flow & Integration Patterns
- API -> Postgres/Neo4j for persistence and graph operations.
- Agents consume/produce messages via RabbitMQ.
- Metrics scraped by Prometheus via `ServiceMonitor`.
- Logs and traces optionally via OTEL Collector.

## Design Decisions and Rationale
- Kustomize overlays for multi-env manageability and minimal duplication.
- ABAC conditions extended for fine-grained security (`api/security/policy.py`).
- Sandbox runtime constraints across services.
- Terraform separates cluster provisioning from in-cluster resources.

## Interface Specifications
- API endpoints documented in `documentation/api/README.md` and tests under `tests/api/`.
- Health endpoints: `/health` (validation), `/metrics` (prometheus when exposed).

## Configuration
- Config via K8s ConfigMap `configmap.yaml` and environment variables.
- Example env files: `.env.*.example` at repo root.

## Diagrams (described)
- Component Diagram: API, Agents, Datastores, MQ, Observability, K8s control plane.
- Data Flow: API read/write to DBs; Agents <-> MQ; Prometheus scrapes services.

See rendered diagrams and source in `documentation/architecture/DIAGRAMS.md`.

Notes:
- Mermaid diagrams render on GitHub automatically.
- PlantUML blocks can be exported via IDE plugins or CI tools.

## Security & Compliance
- RBAC policies (`infrastructure/security/rbac/policies.yaml`).
- Sandbox constraints (`infrastructure/security/docker-compose.override.security.yml`).
- Compliance flags in ConfigMap.

## References
- Planning docs: `documentation/planning/SMAI/*.md`
- Operations: `documentation/operations/`
- Developer Guides: `documentation/developer-guides/`
