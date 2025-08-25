# Enhanced Workflows Guide (n8n)

This guide explains how to import, configure, and validate the enhanced AI workflows located in `workflows/enhanced/`.

## Prerequisites

- n8n (self-hosted) up and running
- API running with environment configured
- Dependencies available:
  - Neo4j 5.x (with APOC recommended)
  - PostgreSQL
  - RabbitMQ (recommended)
  - OpenAI API key

## Files to Import

Import the following workflow JSON files via n8n UI → Import from file:

- `workflows/enhanced/master-orchestration-agent.json`
- `workflows/enhanced/agent-handlers.json`
- `workflows/enhanced/research-agent.json`
- `workflows/enhanced/creative-agent.json`
- `workflows/enhanced/analysis-agent.json`
- `workflows/enhanced/development-agent.json`
- `workflows/enhanced/communication-agent.json`
- `workflows/enhanced/planning-agent.json`
- `workflows/enhanced/execution-agent.json`
- `workflows/enhanced/quality-assurance-agent.json`

## Required Credentials (n8n)

Create credentials for these nodes (or provide via environment):

- OpenAI API (AI Agent nodes)
- Neo4j (bolt URI, username, password)
- PostgreSQL (for task memory persistence)
- RabbitMQ (for agent status events)

Tip: Use environment variables in n8n for consistency across environments.

## API Configuration

Set the following in the API environment (`.env` based on existing examples):

- `N8N_BASE_URL=http://localhost:5678`
- `N8N_API_KEY` (optional if using n8n API)
- `INTEGRATION_SECRET=<shared-token>` (required for inbound run updates)
- `OPENAI_API_KEY=...`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `DATABASE_URL=postgresql+psycopg2://...`
- `RABBITMQ_URL=amqp://guest:guest@localhost:5672/`

## Functional Validation

- Master orchestration flow
  - Trigger via API `POST /agents/{id}/execute` or directly in n8n
  - Observe task delegation to specialized agents
  - Confirm RabbitMQ → WebSocket `agent_run:update` events emitted by API
- Specialized agents
  - Provide representative inputs per agent (research, creative, analysis, etc.)
  - Validate outputs and intermediate error handling nodes
- Persistence & knowledge
  - Verify Neo4j writes/reads for context and knowledge updates
  - Verify Postgres persistence of task runs (AgentRun)

## Troubleshooting

- Credentials unresolved in n8n: ensure each AI/DB/MQ node is bound to a credential
- 401 from API inbound webhook: confirm `INTEGRATION_SECRET` header is present and correct
- Neo4j errors: check `NEO4J_URI` and that APOC is enabled (recommended)
- OpenAI rate limits: reduce concurrency/temperature, or add retries
- RabbitMQ not receiving updates: verify broker connectivity and queue bindings

## Rollout & Backups

- Enhanced workflows reside in `workflows/enhanced/`
- Legacy workflows were backed up under `backup/<timestamp>/workflows_old/`
- Consider feature flags or toggles in your orchestration to swap between legacy and enhanced flows

## Next Steps

- Expand test coverage in `tests/` to exercise orchestration and messaging
- Monitor latency and cost metrics; adjust model parameters accordingly
- Incrementally roll out enhanced flows and gather feedback
