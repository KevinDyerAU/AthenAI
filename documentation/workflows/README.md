# Workflows Guide (n8n)

This guide explains how to author, export, validate, and operate n8n workflows used by NeoV3.

## Structure
- `workflows/analysis-tools/`
- `workflows/communication-tools/`
- `workflows/creative-tools/`
- `workflows/development-tools/`
- `workflows/execution-tools/`
- `workflows/planning-tools/`
- `workflows/qa-tools/`
- `workflows/research-tools/`

## Authoring
1. Build workflows in your n8n instance using credentials (never hardcode secrets in nodes).
2. Add descriptions and notes to key nodes explaining inputs/outputs.
3. Export workflow as JSON (File -> Export) and save in the appropriate directory.

## Conventions
- Include `name`, `nodes`, and `connections` in JSON.
- Use environment variables or n8n credentials for endpoints and tokens.
- Keep small, composable flows; prefer sub-workflows for reuse.
- Name nodes meaningfully; avoid opaque labels.

## Validation
- Validate JSON locally:
  - PowerShell: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/utilities/workflow-validate.ps1`
  - Bash: `bash scripts/utilities/workflow-validate.sh`
- Tests:
  - `python tests/workflows/validate_workflows.py`

## Deployment
- Import workflows into the target n8n environment.
- Map credentials to environment-specific secrets.
- Test using mock/sandbox endpoints before switching to production.

## Troubleshooting
- Missing credentials: ensure n8n credentials are created and mapped.
- HTTP timeouts: increase timeout values or add retries with backoff.
- Webhook verification failures: confirm `N8N_WEBHOOK_SECRET` and clock sync.
