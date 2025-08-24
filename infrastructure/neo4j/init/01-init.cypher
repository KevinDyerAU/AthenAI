// Enhanced AI Agent OS - Neo4j Initialization (Constraints, Indexes, Seed)
// Neo4j 5.x compatible

// ==============================
// Constraints
// ==============================
CREATE CONSTRAINT agent_id IF NOT EXISTS
FOR (a:Agent)
REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT agent_name IF NOT EXISTS
FOR (a:Agent)
REQUIRE a.name IS UNIQUE;

CREATE CONSTRAINT knowledge_id IF NOT EXISTS
FOR (k:Knowledge)
REQUIRE k.id IS UNIQUE;

CREATE CONSTRAINT memory_id IF NOT EXISTS
FOR (m:Memory)
REQUIRE m.id IS UNIQUE;

// ==============================
// Indexes
// ==============================
// Fulltext for knowledge search
CREATE FULLTEXT INDEX knowledge_fulltext IF NOT EXISTS
FOR (k:Knowledge)
ON EACH [k.title, k.content];

// Lookup indexes
CREATE INDEX agent_lookup IF NOT EXISTS
FOR (a:Agent)
ON (a.name);

CREATE INDEX knowledge_agent_lookup IF NOT EXISTS
FOR (k:Knowledge)
ON (k.agentId);

CREATE INDEX memory_agent_lookup IF NOT EXISTS
FOR (m:Memory)
ON (m.agentId);

// Relationship property indexes (Neo4j 5 supports rel indexes)
CREATE INDEX relates_on_type IF NOT EXISTS
FOR ()-[r:RELATES_TO]-()
ON (r.type);

// ==============================
// Optional: n10s (neosemantics) default config
// This will only work if the n10s plugin is present
// CALL n10s.graphconfig.init({ handleVocabUris: "SHORTEN" }) YIELD node RETURN node;

// ==============================
// Seed Data (minimal)
MERGE (a:Agent { name: 'default-agent' })
ON CREATE SET a.id = apoc.create.uuid(),
              a.createdAt = datetime(),
              a.status = 'active';
