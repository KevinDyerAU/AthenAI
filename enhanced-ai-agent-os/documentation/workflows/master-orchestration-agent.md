# Master Orchestration Agent Workflow

Path: `workflows/master-orchestration-agent.json`

## Purpose
Central coordination hub: receives user requests, analyzes task complexity, delegates to appropriate agents, publishes tasks to RabbitMQ, stores/reads context from Neo4j, and maintains conversation memory.

## Endpoints
- Webhook: `POST /webhook/master/orchestrate`
  - Request body example:
    ```json
    {
      "request": "Summarize the latest Neo4j release notes",
      "priority": "high",
      "context": {"userId": "u-123", "sessionId": "s-abc"}
    }
    ```
  - Response (example):
    ```json
    {
      "status": "accepted",
      "primary_agent": "research",
      "collaborators": ["analysis"],
      "queue": "agents.research",
      "plan": ["Collect release notes", "Summarize", "Publish result"],
      "metrics": {"receivedAt": "2025-08-21T00:00:00.000Z"}
    }
    ```

## Node overview
- `Webhook Master Orchestrate` (`n8n-nodes-base.webhook`)
- `AI Agent (Tools)` (`n8n AI Agent` with Tools Agent)
  - Provider: OpenAI `gpt-4` (configurable)
  - Temperature: 0.2
  - System message defines orchestration responsibilities and output JSON schema
  - Tools enabled: HTTP (Node-as-Tools), code disabled by default
- `Validate Orchestration Plan` (Function)
- `Publish → RabbitMQ` (`n8n-nodes-base.rabbitmq`) — publishes orchestration message to selected queue
- `Neo4j Context Write` (`n8n-nodes-base.neo4j`) — optional Cypher execution based on LLM output
- `Conversation Memory Upsert` (Function) — placeholder to persist memory (see below)
- `Build Response` (Function)

## Configuration
- Environment variables (see `.env.example`):
  - RabbitMQ: host, port, user, password
  - Neo4j: host, port, user, password
  - OpenAI/Anthropic keys via n8n credentials
- n8n Credentials:
  - Create credentials for RabbitMQ and Neo4j in n8n and bind the nodes accordingly if required.
  - Configure OpenAI or Anthropic credentials in the AI Agent node.

## Conversation memory
This starter uses a function node as a placeholder to upsert memory. Recommended options:
- Use n8n built-in memory with Postgres persistence, or
- Persist per `sessionId` into Postgres/Neo4j and hydrate into the system prompt on each call.

## RabbitMQ conventions
- Default orchestration queues: `agents.research`, `agents.creative`, `agents.analysis`, etc.
- The AI Agent output must include the `queue` name. Update routing conventions as your team standardizes names.

## Neo4j examples
Example write suggested by the LLM (validate before enabling):
```cypher
MERGE (s:Session {id: $sessionId})
MERGE (r:Request {id: $requestId})
SET r.text = $text, r.createdAt = datetime()
MERGE (s)-[:HAS_REQUEST]->(r)
```

## Metrics
- Add a Prometheus `pushgateway` step or Grafana Loki log line in downstream implementations.
- Current workflow returns `metrics.receivedAt` for quick validation.

## Testing
See `tests/workflows/test-master-orchestration.js` for automated tests. Ensure n8n is running and workflows are imported + activated.
