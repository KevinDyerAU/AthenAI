// Unified Neo4j Graph Schema for NeoV3
// Idempotent: uses IF NOT EXISTS constraints (Neo4j 5+)

// =====================
// Constraints & Indexes
// =====================
CREATE CONSTRAINT knowledge_entity_id IF NOT EXISTS
FOR (n:KnowledgeEntity) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT provenance_id IF NOT EXISTS
FOR (n:Provenance) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT conflict_id IF NOT EXISTS
FOR (n:Conflict) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT user_id IF NOT EXISTS
FOR (n:User) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT embedding_id IF NOT EXISTS
FOR (n:Embedding) REQUIRE n.id IS UNIQUE;

// Helpful lookup indexes
CREATE INDEX knowledge_entity_type IF NOT EXISTS
FOR (n:KnowledgeEntity) ON (n.entity_type);

CREATE INDEX knowledge_updated_at IF NOT EXISTS
FOR (n:KnowledgeEntity) ON (n.updated_at);

CREATE INDEX knowledge_created_at IF NOT EXISTS
FOR (n:KnowledgeEntity) ON (n.created_at);

// Fulltext index for content search (optional)
CREATE FULLTEXT INDEX knowledge_content_fts IF NOT EXISTS
FOR (n:KnowledgeEntity) ON EACH [n.content, n.entity_type];

// Vector index for semantic similarity (Neo4j 5.11+)
// Adjust dimensions and similarity function to match your embedding model
CREATE VECTOR INDEX knowledge_embeddings IF NOT EXISTS
FOR (n:KnowledgeEntity) ON (n.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// =====================
// Node Type Hints
// =====================
// :KnowledgeEntity { id, external_id, entity_type, content, version, updated_at, metadata }
// :Provenance { id, source, evidence, actor_id, created_at, metadata }
// :Conflict { id, field, proposed_value, status, created_at, resolved_at, resolved_by, resolution_note }
// :User { id, username, email }
// :Embedding { id, model, dim, vector } // vector stored as list<float> or external ref
// :KnowledgeSnapshot { id, entity_id, version, content, created_at, metadata }

// =====================
// Relationship Type Hints
// =====================
// (User)-[:CREATED]->(KnowledgeEntity)
// (KnowledgeEntity)-[:HAS_PROVENANCE]->(Provenance)
// (KnowledgeEntity)-[:HAS_CONFLICT]->(Conflict)
// (Conflict)-[:RESOLVED_BY]->(User)
// (KnowledgeEntity)-[:SIMILAR_TO {score:float}]->(KnowledgeEntity)
// (KnowledgeEntity)-[:HAS_EMBEDDING]->(Embedding)
// (KnowledgeEntity)-[:HAS_SNAPSHOT]->(KnowledgeSnapshot)
// (KnowledgeSnapshot)-[:PREVIOUS]->(KnowledgeSnapshot)

// =====================
// Example upsert procedures (safe templates)
// =====================
// Merge KnowledgeEntity by id
// :param id => string
// :param content => string
// :param entity_type => string
// :param version => int
// :param metadata => map
MERGE (ke:KnowledgeEntity {id:$id})
ON CREATE SET ke.content=$content, ke.entity_type=$entity_type, ke.version=$version, ke.created_at=datetime(), ke.updated_at=datetime(), ke.metadata=$metadata
ON MATCH SET ke.content=$content, ke.entity_type=$entity_type, ke.version=$version, ke.updated_at=datetime(), ke.metadata=$metadata;

// Attach provenance
// :param entity_id => string
// :param prov_id => string
// :param source => string
// :param evidence => string
// :param actor_id => string
// :param metadata => map
MATCH (ke:KnowledgeEntity {id:$entity_id})
MERGE (p:Provenance {id:$prov_id})
ON CREATE SET p.source=$source, p.evidence=$evidence, p.actor_id=$actor_id, p.created_at=datetime(), p.metadata=$metadata
MERGE (ke)-[:HAS_PROVENANCE]->(p);

// Log conflict for a field
// :param entity_id => string
// :param conflict_id => string
// :param field => string
// :param proposed_value => any
// :param actor_id => string
MATCH (ke:KnowledgeEntity {id:$entity_id})
MERGE (c:Conflict {id:$conflict_id})
ON CREATE SET c.field=$field, c.proposed_value=$proposed_value, c.status='open', c.created_at=datetime(), c.actor_id=$actor_id
MERGE (ke)-[:HAS_CONFLICT]->(c);

// Snapshot a version for temporal history
// :param entity_id => string
// :param snap_id => string
// :param version => int
// :param content => string
// :param metadata => map
MATCH (ke:KnowledgeEntity {id:$entity_id})
MERGE (s:KnowledgeSnapshot {id:$snap_id})
ON CREATE SET s.entity_id=$entity_id, s.version=$version, s.content=$content, s.created_at=datetime(), s.metadata=$metadata
MERGE (ke)-[:HAS_SNAPSHOT]->(s);
