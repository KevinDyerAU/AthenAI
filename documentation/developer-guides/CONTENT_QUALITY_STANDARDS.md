# Content Quality Standards

These standards ensure scripts, docs, tests, and workflows are clear, complete, and maintainable.

## Scripts
- Header: purpose, usage, prerequisites, exit codes.
- Safety: no destructive ops without confirmations or flags.
- Logging: clear start/end, errors to stderr, verbose mode `-v`.
- Errors: non-zero exit codes; trap/try-catch with actionable messages.
- Cross-platform: provide Bash and PowerShell variants for critical tasks.
- Configuration: read from env vars; do not hardcode secrets.

## Documentation
- Structure: Overview, Prereqs, Setup, Usage, Examples, Troubleshooting, References.
- Clarity: concise, task-oriented steps. Use code blocks.
- Accuracy: keep in sync with code; update alongside changes.
- Links: relative paths to code and scripts.
- Diagrams: include where helpful; store as `.md`/`.drawio` or `.png`.

## Tests
- Deterministic: avoid flaky external dependencies; mock where needed.
- Coverage: unit, integration, e2e, performance, workflows.
- Reporting: write results to `./test-results` in JUnit or markdown summary.
- CI-ready: runnable headless; minimal prerequisites documented.

## Workflows (n8n)
- JSON validity: must parse; include `name`, `nodes`, `connections`.
- Secrets: use credentials in n8n, not literals in JSON.
- Versioning: include `meta.version` or comment file with version/date.
- Documentation: README per directory with purpose and usage.

## Version Control Procedures
- Branch strategy: feature branches -> PR -> review -> main.
- Commits: conventional messages (feat:, fix:, docs:, chore:, test:, refactor:).
- Reviews: require at least 1 review for functional changes.
- Changelogs: summarize in PR description; link issues.
- Tagging: semantic versions for releases.
