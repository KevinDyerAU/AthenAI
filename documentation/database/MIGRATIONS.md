# Database Migrations: Order, Validation, and Automation

This document explains how database schemas are applied and validated during deployment.

## Overview

- Core services start first: `postgres`, `neo4j`, `rabbitmq`.
- After both `postgres` and `neo4j` are healthy, unified schemas are applied automatically by the deploy scripts.
- Subsequent phases start: monitoring stack, `n8n`, and the API service.

## Migration Scripts

- Postgres: `scripts/migrations/apply-postgres.ps1` (Windows) and `scripts/migrations/apply-postgres.sh` (macOS/Linux)
- Neo4j: `scripts/migrations/apply-neo4j.ps1` (Windows) and `scripts/migrations/apply-neo4j.sh` (macOS/Linux)

These scripts:
- Read `.env` for connection details
- Connect to running containers
- Apply idempotent schema files:
  - Postgres: `db/postgres/schema.sql`
  - Neo4j: `db/neo4j/schema.cypher`

## Required Environment

Ensure these keys exist in `.env` at repo root:

- POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- POSTGRES_HOST=postgres, POSTGRES_PORT=5432 (provided by deploy scripts if missing)
- NEO4J_PASSWORD
- RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS

The deploy scripts initialize missing values (and generate secrets) on first run.

## Execution Order

1) Core services up and healthy
2) Apply Postgres schema
3) Apply Neo4j schema
4) Start monitoring, orchestration, API

This order ensures schemas are ready before dependent services come online.

## How to Run

- Windows PowerShell:
  ```powershell
  .\deploy-local.ps1 -Fresh   # full reset + auto migrations
  .\deploy-local.ps1          # reuse environment + auto migrations
  ```
- macOS/Linux Bash:
  ```bash
  ./deploy-local.sh --fresh    # full reset + auto migrations
  ./deploy-local.sh            # reuse environment + auto migrations
  ```

To run migrations manually (rare):
- Windows: `scripts/migrations/apply-postgres.ps1` then `scripts/migrations/apply-neo4j.ps1`
- Bash: `scripts/migrations/apply-postgres.sh` then `scripts/migrations/apply-neo4j.sh`

## Validation Steps

- Postgres:
  - Verify schema version table exists: `SELECT * FROM schema_migrations;`
  - Check key tables (e.g., `users`, `conversations`, `knowledge_entities`) exist
- Neo4j:
  - Verify constraints: `SHOW CONSTRAINTS;`
  - Verify indexes: `SHOW INDEXES;`

The deploy scripts log outcomes to `deployment.local.log`.

## Troubleshooting

- Missing passwords: ensure `.env` has `POSTGRES_PASSWORD` and `NEO4J_PASSWORD`. Run `-Fresh/--fresh` if needed to regenerate.
- Containers not healthy: check `docker compose ps` and container logs. The deploy scripts wait for health before running migrations.
- Permission errors (psql): the scripts pass `PGPASSWORD` automatically; ensure the user/db match container ENV.

## Safety and Idempotency

- SQL and Cypher are designed to be idempotent (CREATE IF NOT EXISTS, MERGE patterns)
- Scripts are safe to re-run; they will not drop or modify existing records.
