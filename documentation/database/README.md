# Database Overview

This section documents Neo4j and Postgres usage within NeoV3.

## Neo4j
- URI: `bolt://neo4j:7687`
- Auth: `NEO4J_USER` / `NEO4J_PASSWORD` (from `.env`)
- Data model: Knowledge graph with `KnowledgeEntity` nodes and relationships such as `HAS_PART`.
- Example queries:
```cypher
MATCH (d:KnowledgeEntity {id:'doc-n8n-guide'}) RETURN d LIMIT 1;
MATCH (d:KnowledgeEntity {id:'doc-n8n-guide'})-[:HAS_PART]->(c:KnowledgeEntity {entity_type:'chunk'}) RETURN count(c);
```

## Postgres
- URL in API: `DATABASE_URL` (psql URL built from `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`)
- Used by the API for relational needs and metrics storage hooks.

## Environment variables
- Neo4j: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- Postgres: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`

See `documentation/configuration/ENVIRONMENT_CONFIG.md` for the exhaustive list and defaults.
