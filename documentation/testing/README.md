# Testing Guide

This guide describes how to run and extend the test suites.

## Categories
- Unit: fast, isolated component tests.
- Integration: cross-component checks (e.g., config validation, workflow JSON).
- E2E: end-to-end flows (see enhanced suite).
- Performance: load and latency checks.
- AI Capabilities: provider/config sanity.
- Workflows: n8n workflow JSON validation and conventions.

## Quick start (Windows)
- PowerShell consolidated:
```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/testing/run-local-tests.ps1
```
- Category runners:
```
powershell -NoProfile -ExecutionPolicy Bypass -File tests/unit/run.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tests/integration/run.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tests/workflows/run.ps1
```

## Quick start (Bash)
```
bash scripts/testing/run-local-tests.sh
```

## Integration checks included
- Environment template validation using `scripts/config/validate_env.py`.
- Workflow JSON validation via `tests/workflows/validate_workflows.py` and utility scripts.

## Writing new tests
- Prefer deterministic tests; avoid external calls when possible.
- Output results to `./test-results`.
- Follow `documentation/developer-guides/CONTENT_QUALITY_STANDARDS.md`.
