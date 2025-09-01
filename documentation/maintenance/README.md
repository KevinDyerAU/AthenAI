# Maintenance and Knowledge Base

This section documents routine maintenance, backups, and knowledge base references.

- See `MAINTENANCE_AND_KB.md` for detailed procedures.
- Common tasks:
  - Checking container health and logs
  - Backups (Postgres, Neo4j), see `scripts/backup/`
  - Grafana/Prometheus data retention basics

## Environment references
- See `documentation/configuration/ENVIRONMENT_CONFIG.md` for all variables.
- Services read `.env` at repo root.

## Useful commands
```bash
# Containers
./deploy-local.sh --status

docker compose ps

docker logs -f enhanced-ai-agent-api
```
