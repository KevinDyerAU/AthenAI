# Research Agent

Purpose: multi-source research orchestration combining web and academic search, content analysis, credibility scoring, AI synthesis, and optional Neo4j graph update.

- Workflow: `workflows/research-agent.json`
- Webhook: `POST /webhook/research/query`

## Prerequisites
- OpenAI credentials in n8n
- Optional: Neo4j credential named `neo4j`

## Request
```json
POST /webhook/research/query
{
  "query": "latest developments in retrieval-augmented generation",
  "maxResults": 6,
  "timeframe": "2y"
}
```

## Response (shape)
- `report`: structured JSON with executive summary, findings, citations, confidence, next steps
- `status`: ok

## Internals
- Web + Academic search -> URL collection -> Content analysis -> Credibility scoring -> AI synthesis -> Shape output -> Neo4j update

## Recommended Next Steps
- Add server-side search keys and quotas management
- Add configurable domain allow/deny lists for credibility heuristics
- Expand synthesis to include counterarguments and dissenting sources
- Add tests for long-tail queries and failure paths
- Add rate-limit/backoff policies and caching layer
