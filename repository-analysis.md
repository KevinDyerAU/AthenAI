# Repository Structure Analysis and Cleanup Plan

Generated: 2025-08-24 03:31:33 +10:00

---

## Executive Summary

This repo contains two parallel implementations/structures:

- Root implementation ("NeoV3 root"): `api/`, `infrastructure/`, `scripts/`, `tests/`, `workflows/`, `documentation/`, `.github/workflows/ci.yml`.
- Enhanced implementation ("Enhanced AI Agent OS"): `enhanced-ai-agent-os/` with its own `documentation/`, `infrastructure/`, `scripts/`, `tests/`, `workflows/`, and Docker Compose files.

There are overlapping domains (monitoring, documentation, workflows, tests, scripts, environment/config), and some duplicates (sample workflow templates vs concrete agent workflows). This document inventories the repository, identifies conflicts, and recommends a consolidation path. A safe cleanup plan with backups is provided.

---

## Inventory

### Root level

- `.github/workflows/ci.yml`
- Environment examples: `.env.example`, `.env.development.example`, `.env.production.example`
- `README.md`
- `complete_implementation_guide.md`
- `api/`
  - `openapi.yaml`
  - models/resources/schemas/security/... (FastAPI/Flask-style structure observed)
- `documentation/`
  - `api/`, `configuration/`, `developer-guides/`, `monitoring/`, `operations/`, `security/`, `testing/`, `workflows/`
- `infrastructure/`
  - `monitoring/` (Prometheus/Grafana/Alertmanager configs, docker-compose for monitoring)
  - `security/` (jwt, nginx, rbac, tls readme)
- `scripts/`
  - `backup/`, `config/`, `maintenance/`, `monitoring/`, `n8n/`, `neo4j/`, `security/`, `setup/`, `testing/`, `utilities/`, `verification/`
- `tests/`
  - `ai-capabilities/`, `api/`, `e2e/`, `integration/`, `performance/`, `security/`, `unit/`, `workflows/`
- `workflows/`
  - Multiple tool folders each with `README.md` and `sample-workflow.json` templates

Docker Compose in root tree:
- `infrastructure/monitoring/docker-compose.monitoring.yml`

YAML/Config in root tree (selected):
- `infrastructure/monitoring/*` (prometheus.yml, grafana datasource/dashboards yaml, alertmanager.yml, otel/collector.yaml, custom metrics, rules)

### `enhanced-ai-agent-os/`

- `.env.example`
- `README.md`
- Docker Compose: `docker-compose.yml`, `docker-compose.prod.yml`
- `deploy-cloud/` (Render.com guide + script)
- `deploy-local/` (local guide + script)
- `documentation/`
  - mirrors root topics: `api/`, `configuration/`, `developer-guides/`, `monitoring/`, `operations/`, `testing/`, plus `workflows/`
- `infrastructure/`
  - `database/`, `monitoring/`, `n8n/`, `neo4j/`, `nginx/`, `postgres/`, `rabbitmq/`
  - monitoring contains alertmanager, grafana, loki/promtail, prometheus (with rules), targets, etc.
- `scripts/`
  - `backup/`, `maintenance/`, `monitoring/`, `security/`, `setup/`, `testing/`, `utilities/`, `scripts-pwsh-helpers.ps1`, `validate-environment.sh`
- `tests/`
  - `ai-capabilities/`, `e2e/`, `integration/`, `performance/`, `unit/`, `workflows/`
- `workflows/`
  - Concrete agent JSONs (e.g., `analysis-agent.json`, `research-agent.json`, `master-orchestration-agent.json`, etc.) and tool subfolders

---

## Overlaps and Conflicts

1. Workflows content
   - Root `workflows/` contains templates: each tool folder has `README.md` and `sample-workflow.json`.
   - `enhanced-ai-agent-os/workflows/` contains concrete agent workflows and similar tool subfolders.
   - Risk: duplicated conceptual space; users may be confused which is source of truth.

2. Monitoring stack
   - Root `infrastructure/monitoring/` includes Prometheus, Grafana, Alertmanager, OTEL collector, custom metrics, and `docker-compose.monitoring.yml`.
   - `enhanced-ai-agent-os/infrastructure/monitoring/` also includes Prometheus, Grafana, Alertmanager, Loki/Promtail, rules and targets.
   - Risk: divergent configs and rule sets; two places to maintain.

3. Docker Compose
   - Root: monitoring-only compose (`infrastructure/monitoring/docker-compose.monitoring.yml`).
   - Enhanced: full system compose files (`docker-compose.yml`, `docker-compose.prod.yml`).
   - Risk: partial vs complete stack definitions in different locations; potential port/volume conflicts.

4. Documentation
   - Root `documentation/` mirrors topics present in `enhanced-ai-agent-os/documentation/`.
   - Risk: drift and duplication; which README is canonical?

5. Tests
   - Root `tests/` and `enhanced-ai-agent-os/tests/` have similar category subfolders.
   - Risk: duplicated or divergent test suites; CI may run one but not the other.

6. Scripts
   - Root `scripts/` and `enhanced-ai-agent-os/scripts/` include similar categories (backup, monitoring, setup, testing, utilities).
   - Risk: duplication and drift; different helper names.

7. Environment examples
   - Root: `.env.example`, `.env.development.example`, `.env.production.example`.
   - Enhanced: `enhanced-ai-agent-os/.env.example`.
   - Risk: mismatch in variable naming and defaults; unclear which to use when deploying the combined system.

8. CI workflows
   - Only root `.github/workflows/ci.yml` found. No separate GitHub Actions under `enhanced-ai-agent-os/`.
   - Not a conflict, but ensure CI targets the canonical paths post-merge.

---

## Recommendations (by area)

1. Workflows
   - Preserve: `enhanced-ai-agent-os/workflows/` as the canonical set of runnable agent workflows.
   - Preserve in root: `workflows/*/README.md` as general docs if useful.
   - Deprecate: root `workflows/*/sample-workflow.json` templates once consolidated examples exist in Enhanced.
   - Action: move deprecated templates to backup; add a single pointer README in root `workflows/` directing users to Enhanced workflows.

2. Monitoring
   - Decide a single canonical monitoring stack. Recommendation: use `enhanced-ai-agent-os/infrastructure/monitoring/` (more complete: includes Loki/Promtail and Prometheus rules, targets).
   - Merge any unique root rules or dashboards into the Enhanced monitoring set.
   - Deprecate: `infrastructure/monitoring/docker-compose.monitoring.yml` if redundant with Enhanced compose services, or relocate it under `enhanced-ai-agent-os/infrastructure/monitoring/` if kept as a "monitoring-only" profile.

3. Docker Compose
   - Preserve: `enhanced-ai-agent-os/docker-compose.yml` and `docker-compose.prod.yml` as canonical orchestrations.
   - Document: a path to run monitoring-only via profiles or a dedicated `docker-compose.monitoring.yml` colocated with Enhanced infra, if needed.

4. Documentation
   - Choose a single documentation tree to maintain. Recommendation: consolidate into root `documentation/` and link sections that are specific to Enhanced to live under `documentation/` or move Enhanced-specific docs into root, then delete duplicates.
   - Near-term: keep Enhanced docs as source while migrating content to root; add pointers to avoid confusion.

5. Tests
   - Consolidate tests under a single `tests/` hierarchy at the root. Migrate any Enhanced-only tests that reference Enhanced paths; adjust imports.
   - Remove empty or obsolete categories; ensure CI (`.github/workflows/ci.yml`) runs the unified test suite.

6. Scripts
   - Consolidate into root `scripts/`. Merge unique helper scripts from Enhanced; avoid duplicate names. Keep cross-platform support (PowerShell + Bash) if present.
   - Provide a `scripts/README.md` describing purpose and usage.

7. Environment examples
   - Create a single authoritative `.env.example` at the repo root combining variables from both sets.
   - Keep environment matrix files as needed: `.env.development.example`, `.env.production.example`.
   - Remove `enhanced-ai-agent-os/.env.example` after the merge, replacing it with a pointer to root.

8. CI
   - Keep `.github/workflows/ci.yml` and update to reference the unified directories. Add matrix jobs for compose linting and workflow validation if applicable.

---

## Specific Conflicts and Resolutions

- Duplicate workflow examples
  - Conflict: Root `workflows/*/sample-workflow.json` vs Enhanced concrete agent workflows.
  - Resolution: Keep Enhanced concrete workflows. Move root sample JSONs to backup; optionally keep one or two curated examples in root referencing Enhanced.

- Monitoring configs and rules
  - Conflict: `infrastructure/monitoring/*` vs `enhanced-ai-agent-os/infrastructure/monitoring/*`.
  - Resolution: Keep Enhanced as base. Review root-only files:
    - `infrastructure/monitoring/otel/collector.yaml` (keep if OTEL collector needed; integrate under Enhanced infra tree).
    - `infrastructure/monitoring/custom-metrics/ai_metrics.yaml` (merge into Enhanced Prometheus scrape/configs if unique).
    - Grafana provisioning YAMLs: compare and merge unique dashboards/datasources.

- Docker Compose
  - Conflict: Enhanced full stack vs root monitoring-only compose.
  - Resolution: Keep Enhanced docker-compose files; either drop root monitoring compose or move under Enhanced infra as an optional profile.

- Documentation duplication
  - Conflict: Topic mirrors in both trees.
  - Resolution: Keep root `documentation/` as canonical. Migrate Enhanced docs; then remove duplicates.

- Environment files
  - Conflict: Root `.env.*.example` vs `enhanced-ai-agent-os/.env.example`.
  - Resolution: Create canonical root `.env.example` that includes superset. Remove Enhanced one after migration.

- Tests duplication
  - Conflict: Root vs Enhanced `tests/`.
  - Resolution: Unify under root. Migrate Enhanced tests and delete Enhanced tests after migration.

- Scripts duplication
  - Conflict: Root vs Enhanced `scripts/`.
  - Resolution: Unify under root; migrate unique Enhanced scripts; remove duplicates.

---

## Immediate, Safe Cleanup Candidates (low risk)

- Root workflow templates: `workflows/*/sample-workflow.json` (8 files). Rationale: clearly labeled samples; concrete workflows exist under Enhanced.
- Orphaned gitkeep: `enhanced-ai-agent-os/workflows/.gitkeep` (redundant given populated directory).
- Empty directories under `enhanced-ai-agent-os/` (`backups/`, `data/`, `logs/`) — remove only if confirmed unused by scripts.

These will be backed up before removal.

---

## Backup Strategy

- Create `backup/` at repo root.
- Use timestamped subfolder: `backup/20250824-033133/` (YYYYMMDD-HHMMSS local time).
- Mirror original paths under backup to preserve context.
- Record a `CHANGELOG.md` in the backup folder summarizing moved items and rationale.

Example structure after first pass:
```
backup/20250824-033133/
  workflows/analysis-tools/sample-workflow.json
  workflows/communication-tools/sample-workflow.json
  ...
  enhanced-ai-agent-os/workflows/.gitkeep
```

---

## Proposed Commands (PowerShell)

Note: commands below move files into a timestamped backup folder; review before execution.

```powershell
# Variables
$ts = "20250824-033133"
$dest = Join-Path -Path "$PSScriptRoot" -ChildPath "backup/$ts"

# Ensure backup directory exists
New-Item -ItemType Directory -Path $dest -Force | Out-Null

# 1) Backup root workflow sample JSONs
$samplePaths = @(
  "workflows/analysis-tools/sample-workflow.json",
  "workflows/communication-tools/sample-workflow.json",
  "workflows/creative-tools/sample-workflow.json",
  "workflows/development-tools/sample-workflow.json",
  "workflows/execution-tools/sample-workflow.json",
  "workflows/planning-tools/sample-workflow.json",
  "workflows/qa-tools/sample-workflow.json",
  "workflows/research-tools/sample-workflow.json"
)
foreach ($rel in $samplePaths) {
  $src = Join-Path -Path "$PSScriptRoot" -ChildPath $rel
  if (Test-Path $src) {
    $target = Join-Path -Path $dest -ChildPath $rel
    New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null
    Move-Item -Path $src -Destination $target -Force
  }
}

# 2) Backup orphaned gitkeep in Enhanced workflows
$gitkeep = Join-Path -Path "$PSScriptRoot" -ChildPath "enhanced-ai-agent-os/workflows/.gitkeep"
if (Test-Path $gitkeep) {
  $target = Join-Path -Path $dest -ChildPath "enhanced-ai-agent-os/workflows/.gitkeep"
  New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null
  Move-Item -Path $gitkeep -Destination $target -Force
}

# 3) (Optional) backup empty dirs if verified unused
$maybeEmpty = @(
  "enhanced-ai-agent-os/backups",
  "enhanced-ai-agent-os/data",
  "enhanced-ai-agent-os/logs"
)
foreach ($rel in $maybeEmpty) {
  $path = Join-Path -Path "$PSScriptRoot" -ChildPath $rel
  if (Test-Path $path) {
    if ((Get-ChildItem -Path $path -Recurse | Measure-Object).Count -eq 0) {
      $target = Join-Path -Path $dest -ChildPath $rel
      New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null
      Move-Item -Path $path -Destination $target -Force
    }
  }
}

# 4) Write backup changelog
$log = @()
$log += "Backup timestamp: $ts"
$log += "Backed up root sample workflows and minor artifacts to backup/$ts"
$log | Set-Content -Path (Join-Path $dest 'CHANGELOG.md')
```

---

## Next Steps (Phased)

- Phase 1 (Low risk)
  - Backup and remove root `sample-workflow.json` files.
  - Remove orphaned `.gitkeep` under Enhanced workflows.

- Phase 2 (Consolidation)
  - Choose canonical monitoring under Enhanced; migrate root unique configs (OTEL collector, custom metrics) into Enhanced infra.
  - Deprecate root `infrastructure/monitoring/docker-compose.monitoring.yml` or move it under Enhanced infra as optional profile.

- Phase 3 (Docs/Env/Scripts/Tests)
  - Merge docs into root; add pointers; remove Enhanced duplicates.
  - Create unified `.env.example` at root and remove Enhanced `.env.example`.
  - Consolidate scripts and tests at root; update CI.

- Phase 4 (Validation)
  - Run CI, compose validations, monitoring stack boot check, and end-to-end tests.

---

## Validation Checklist

- Critical files preserved:
  - Root: `api/`, `.github/workflows/ci.yml`, env examples, top-level docs.
  - Enhanced: `docker-compose.yml` and `docker-compose.prod.yml`, `infrastructure/monitoring/`, concrete `workflows/` JSONs.
- No active configs removed without backup.
- Repository tree simplified; single canonical location per concern.
- All changes logged in `backup/<timestamp>/CHANGELOG.md` and summarized in PR description.
