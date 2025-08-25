# Consciousness Substrate (Neo4j) — Quick Usage

This document summarizes the enhanced Neo4j schema and how to use the substrate via the API.

## Schema summary

Nodes and indexes defined in `db/neo4j/schema.cypher`:

- KnowledgeEntity(id, content, entity_type, version, metadata, embedding, created_at, updated_at)
- Provenance(action, actor, at, details)
- Conflict(strategy, at, details)
- KnowledgeSnapshot(version, at, diff)
- Indexes
  - Constraints on ids and timestamps
  - Fulltext for content/name
  - Vector index on `KnowledgeEntity.embedding` (1536 dims, cosine)

Recommended: Neo4j 5.x with APOC and (optionally) GDS for graph algorithms.

## Apply schema

Run from Neo4j Browser or cypher-shell:

```bash
cat db/neo4j/schema.cypher | cypher-shell -u $NEO4J_USER -p $NEO4J_PASSWORD -a $NEO4J_URI
```

## API endpoints

Registered under the RESTX API at `/api/substrate/*`:

- POST `/api/substrate/entity` → create entity with provenance
- PATCH `/api/substrate/entity/{entity_id}` → update with conflict strategy: `merge|latest_wins|first_wins|strict`
- POST `/api/substrate/search/semantic` → vector similarity over `embedding`
- GET `/api/substrate/provenance/{entity_id}` → history
- POST `/api/substrate/traverse` → related nodes (depth/rel-type filters)
- POST `/api/substrate/graph/centrality` → PageRank (GDS) with fallback
- POST `/api/substrate/graph/communities` → Louvain (GDS) with fallback
- GET `/api/substrate/temporal/{entity_id}` → timeline (provenance + snapshots)

All endpoints require JWT.

## Environment

- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- Optional vector search (if you embed content outside the API):
  - `ENABLE_VECTOR_SEARCH=true`
  - Ensure 1536-dim `embedding` is stored on `KnowledgeEntity`

## Python utility

Use `api/utils/consciousness_substrate.py` directly for programmatic access. Key methods:

- `create_knowledge_entity(...)`
- `update_knowledge_entity(..., conflict_resolution="merge")`
- `semantic_search(query_embedding, limit, threshold)`
- `traverse_related(...)`, `centrality_pagerank(...)`, `community_detection_louvain(...)`
- `temporal_evolution(entity_id, since_iso=None, until_iso=None)`

## Sync with PostgreSQL

A scaffold for bidirectional sync is provided:

- Service: `api/services/knowledge_sync.py`
- Example SQLAlchemy wiring: `api/services/pg_sqlalchemy_wiring_example.py`

Wire your ORM models via provided factory helpers and call:

```python
svc.sync_pg_to_neo4j(transform_to_updates=lambda row: (row["id"], row))
svc.sync_neo4j_to_pg(list_neo4j_entities=..., transform_to_pg=lambda n: n)
```

## Tests

Integration tests for endpoints: `tests/api/test_substrate_endpoints.py`
- Skips gracefully if Neo4j is unavailable or vector index isn’t configured.
