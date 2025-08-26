# Training Materials and Knowledge Transfer

## Curriculum Outline
1. Architecture & Design (review `documentation/architecture/README.md` and SMAI planning docs)
2. Deployment & Operations (`documentation/operations/DEPLOYMENT_AND_OPERATIONS.md`)
3. Developer & Integration (`documentation/developer-guides/DEVELOPER_INTEGRATION_GUIDE.md`)
4. User & Admin (`documentation/user/USER_ADMIN_GUIDE.md`)
5. Security & Compliance (RBAC/ABAC, sandbox, secrets)
6. Observability (Prometheus/Grafana, ServiceMonitor)

## Hands-on Labs
- Lab 1: Provision dev cluster and deploy dev overlay.
- Lab 2: Build and push new API image; deploy via workflow with validation.
- Lab 3: Create and deploy a new agent service and ServiceMonitor.
- Lab 4: Trigger and analyze HPA scaling using load.

## Knowledge Transfer Procedures
- Documentation walkthrough sessions.
- Pairing on one full deploy cycle (dev → prod dry run).
- Checklists and runbooks review.
- Knowledge validation: run `validate.sh` and interpret outputs; perform controlled rollback.

## Materials
- Slides (to be created as needed) summarizing architecture and operations.
- Recorded demos (optional): deployment, validation, rollback.
