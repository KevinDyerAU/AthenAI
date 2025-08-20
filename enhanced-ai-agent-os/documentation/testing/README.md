# Testing Framework

Comprehensive test suites validate functionality across units, integrations, end-to-end flows, performance, and AI capabilities.

## Structure
- `enhanced-ai-agent-os/tests/unit/` — Fast checks of workflow JSON and utilities
- `enhanced-ai-agent-os/tests/integration/` — Cross-workflow presence and contracts
- `enhanced-ai-agent-os/tests/e2e/` — Webhook endpoint smoke tests against running n8n
- `enhanced-ai-agent-os/tests/performance/` — Load tests via k6/ab/curl
- `enhanced-ai-agent-os/tests/ai-capabilities/` — AI provider config + minimal external checks
- `enhanced-ai-agent-os/scripts/testing/run-all-tests.sh` — Orchestrator

## Prerequisites
- bash, curl, jq
- Optional: k6 or ApacheBench (ab) for performance; docker for env; trivy/trufflehog for security
- n8n running for e2e/performance (skips gracefully if unreachable)

## Running tests
- All categories:
  ```bash
  bash enhanced-ai-agent-os/scripts/testing/run-all-tests.sh --category all --results-dir ./test-results
  ```
- Individual categories:
  ```bash
  bash enhanced-ai-agent-os/scripts/testing/run-all-tests.sh --category unit
  bash enhanced-ai-agent-os/scripts/testing/run-all-tests.sh --category integration
  bash enhanced-ai-agent-os/scripts/testing/run-all-tests.sh --category e2e
  bash enhanced-ai-agent-os/scripts/testing/run-all-tests.sh --category performance
  bash enhanced-ai-agent-os/scripts/testing/run-all-tests.sh --category ai
  ```

## Environment
- Set `N8N_BASE_URL` for endpoint tests (default: `http://localhost:5678`).
- Provide `.env` (or `ENV_FILE`) for AI capability tests.

## Results & Metrics
- Summary log written to `--results-dir` with pass/fail per test.
- Performance script outputs request counts and average latency; k6/ab provide richer metrics when available.
- Integrate with CI by running the orchestrator and archiving the `test-results` directory.

## Windows usage
- Use PowerShell wrapper:
  ```powershell
  powershell -ExecutionPolicy Bypass -File enhanced-ai-agent-os\scripts\testing\run-all-tests.ps1 --category all --results-dir .\test-results
  ```

## CI suggestions
- In GitHub Actions, run on push/PR:
  - Setup bash/jq
  - Optionally start n8n via Docker for e2e/perf stages
  - Run `run-all-tests.sh` with `--category all`
  - Upload `test-results` as artifacts
