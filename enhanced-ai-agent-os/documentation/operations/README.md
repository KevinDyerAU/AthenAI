# Operations Guide

This directory documents operational procedures for the Enhanced AI Agent OS, including setup, monitoring, backup, maintenance, security, and workflow management.

## Prerequisites
- Bash shell (use Git Bash or WSL on Windows)
- curl, jq
- Optional: docker, docker compose, pg_dump, redis-cli, cypher-shell or neo4j-admin, aws CLI, trivy, trufflehog

## Setup & Installation
- **Install system**: `enhanced-ai-agent-os/scripts/setup/install-system.sh`
  - Docker mode (recommended):
    ```bash
    bash enhanced-ai-agent-os/scripts/setup/install-system.sh --mode docker --env-file .env
    ```
  - Local mode:
    ```bash
    bash enhanced-ai-agent-os/scripts/setup/install-system.sh --mode local --env-file .env
    ```
- **Configure environment**: `enhanced-ai-agent-os/scripts/setup/configure-environment.sh`
  ```bash
  bash enhanced-ai-agent-os/scripts/setup/configure-environment.sh --env development
  bash enhanced-ai-agent-os/scripts/setup/configure-environment.sh --env production --set N8N_BASE_URL=https://n8n.example.com
  ```

## Environment Validation
- `enhanced-ai-agent-os/scripts/validate-environment.sh`
  ```bash
  bash enhanced-ai-agent-os/scripts/validate-environment.sh --env-file .env
  ```

## Monitoring & Health
- **Health check**: `enhanced-ai-agent-os/scripts/monitoring/health-check.sh`
  ```bash
  N8N_BASE_URL=http://localhost:5678 bash enhanced-ai-agent-os/scripts/monitoring/health-check.sh
  ```

## Backup & Recovery
- **Backup all**: `enhanced-ai-agent-os/scripts/backup/backup-all-data.sh`
  ```bash
  bash enhanced-ai-agent-os/scripts/backup/backup-all-data.sh --output-dir ./backups --include all
  # Upload to S3
  bash enhanced-ai-agent-os/scripts/backup/backup-all-data.sh --output-dir ./backups --include all --s3
  ```

## Maintenance & Logs
- **Log analysis**: `enhanced-ai-agent-os/scripts/maintenance/log-analysis.sh`
  ```bash
  bash enhanced-ai-agent-os/scripts/maintenance/log-analysis.sh --path ./audit.log --top-errors --rotate --clean-days 30
  ```

## Security & Compliance
- **Security scan**: `enhanced-ai-agent-os/scripts/security/security-scan.sh`
  ```bash
  # Validate env, audit npm, scan image, and secret scan repo
  bash enhanced-ai-agent-os/scripts/security/security-scan.sh --env-file .env --npm-audit --docker-image n8nio/n8n:latest --trufflehog .
  ```

## Workflow Management (n8n API)
- `enhanced-ai-agent-os/scripts/utilities/workflow-management.sh`
  ```bash
  # List
  bash enhanced-ai-agent-os/scripts/utilities/workflow-management.sh --api-url http://localhost:5678 --api-key XXXXX list
  # Export
  bash enhanced-ai-agent-os/scripts/utilities/workflow-management.sh --api-url http://localhost:5678 --api-key XXXXX export --out-dir ./wf
  # Import & activate
  bash enhanced-ai-agent-os/scripts/utilities/workflow-management.sh --api-url http://localhost:5678 --api-key XXXXX import --in-dir ./wf --activate
  ```

## Notes
- On Windows, use Git Bash or WSL.
- Never commit real secrets. Use a secret manager in production.
