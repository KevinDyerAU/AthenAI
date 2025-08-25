# Enhanced n8n AI Workflows

This folder contains enhanced n8n workflow templates that leverage modern, built-in AI capabilities for sophisticated agent coordination and task execution.

Key components:
- Enhanced Master Orchestration (AI agent-based)
- Specialized agent workflows (Research, Creative, Analysis, Development, Communication, Planning, Execution, QA)
- Node-as-Tools registry enabling dynamic tool usage

Important: Node names/types for AI nodes vary by n8n version. Use the latest built-in AI nodes (e.g., AI Agent / AI Chat Model) and map parameters accordingly when importing.

## Prerequisites
- n8n >= 1.50 (or latest) with built-in AI nodes enabled
- Access to LLM provider(s) (e.g., OpenAI) configured in n8n credentials
- RabbitMQ reachable by n8n (for delegation messages)
- API base URL and `INTEGRATION_SECRET` for inbound run status updates (`POST /integrations/n8n/runs`)

## Integration with API and Messaging
- Outbound: Master and agents publish delegation and status via RabbitMQ queues (e.g., `agent_delegation`). API also triggers n8n via its webhooks where applicable.
- Inbound: n8n invokes `POST /integrations/n8n/runs` with `X-Integration-Token: INTEGRATION_SECRET` to update run status; API emits WebSocket `agent_run:update`.
- WebSockets: Real-time updates forwarded to rooms `agent:{agent_id}` and `{execution_id}`.

## Node-as-Tools
- See `tool-registry.json` for a curated catalog of common n8n nodes (HTTP, Postgres, Neo4j, RabbitMQ, Files, Math, etc.).
- AI agents are prompted with tool descriptions and parameter schemas. Use n8n Function/Code nodes to map selected tool parameters to the actual node properties at runtime.
- Recommended pattern:
  1) AI Agent produces an action `{ tool: <name>, params: { ... } }`
  2) Validate params against registry schema
  3) Route to the corresponding node with mapped fields
  4) Capture result/errors; feed back to the agent for reflection/retry

## Files
- `master_enhanced_orchestration.json` — Master orchestration AI agent workflow
- `agents/*.json` — Specialized agent templates
- `tool-registry.json` — Node-as-Tools registry

## Validation Steps
- Test with diverse tasks; verify decisions and dynamic tool usage
- Confirm knowledge reads/writes with Neo4j substrate
- Validate error handling and recovery branches
- Monitor performance and resource utilization in n8n and API logs

## Import Instructions
1. In n8n, click Import from file for each JSON in this folder.
2. Edit AI node types to your n8n version (e.g., replace placeholders with built-in AI nodes).
3. Wire credentials (OpenAI, Postgres, Neo4j, RabbitMQ) to corresponding nodes.
4. Configure environment variables in n8n for API base URL and `INTEGRATION_SECRET`.
