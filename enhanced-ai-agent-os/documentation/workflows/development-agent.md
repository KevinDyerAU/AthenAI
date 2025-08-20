# Development Agent Workflow

- __Purpose__: Code generation, architecture, testing, security, and deployment automation across multiple languages.
- __Entry__: `POST /webhook/development/run`
- __Tools__: Code Generation, Testing Automation, Deployment Automation

## Nodes
- __Webhook Development Input__: receives `{ requirements, languages?, repo?, project?, options? }`.
- __Normalize Input__: validates and shapes inputs.
- __Code Generation__: `/webhook/development/tools/code-generation` creates scaffolds and plan.
- __Testing Automation__: `/webhook/development/tools/testing-automation` provides strategies and CI checks.
- __Deployment Automation__: `/webhook/development/tools/deployment-automation` provides CI/CD and env plans.
- __AI Synthesize Dev Plan__: composes structured JSON plan consolidating all pieces.
- __Respond__: returns `{ status, plan, codegen, testing, deployment }`.

## Example Request
```json
{
  "requirements": "Build a REST API with auth, CRUD, tests, CI/CD",
  "languages": ["python", "javascript", "go"],
  "repo": {"provider": "github", "url": "https://github.com/acme/project"},
  "project": {"name": "service", "stack": "python"}
}
```

## Tool Contracts
- __Code Generation__ (POST): returns `{ codegen: { plan, starterFiles } }`.
- __Testing Automation__ (POST): returns `{ testing: { strategies, qualityGates, ciSteps } }`.
- __Deployment Automation__ (POST): returns `{ deployment: { cicd, environments, deployTemplates } }`.

## Outputs
- __plan__: structured JSON with `architecture, components, code_scaffolds, quality_checks, security_scans, testing_plan, ci_cd, docs_plan, risks, performance, metrics, next_steps`.

## Notes
- Configure credentials for the AI node provider (e.g., OpenAI) in n8n.
- Replace Function tool nodes with dedicated services for deeper static analysis, SCA, SAST/DAST, or IaC scanning as needed.
