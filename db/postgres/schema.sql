-- Unified PostgreSQL Schema for NeoV3
-- Safe to run multiple times (uses IF EXISTS/IF NOT EXISTS where possible)

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;           -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pg_trgm;            -- FTS helpers
CREATE EXTENSION IF NOT EXISTS vector;             -- pgvector

-- =====================
-- Schema Versioning
-- =====================
CREATE TABLE IF NOT EXISTS schema_migrations (
  id BIGSERIAL PRIMARY KEY,
  version VARCHAR(100) NOT NULL,
  description TEXT,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================
-- User Management
-- =====================
CREATE TABLE IF NOT EXISTS roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_roles (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255),
  key_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_used_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS auth_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  user_agent TEXT,
  ip_address INET,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,
  revoked BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,
  revoked BOOLEAN DEFAULT FALSE
);

-- =====================
-- Conversations
-- =====================
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255),
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  metadata JSONB
);

CREATE TABLE IF NOT EXISTS conversation_participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(50) DEFAULT 'participant',
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  sender_id UUID REFERENCES users(id),
  content TEXT NOT NULL,
  content_tsv tsvector,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB
);

-- FTS trigger for messages
CREATE OR REPLACE FUNCTION messages_tsv_trigger() RETURNS trigger AS $$
BEGIN
  NEW.content_tsv := to_tsvector('english', coalesce(NEW.content,''));
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_messages_tsv ON messages;
CREATE TRIGGER trg_messages_tsv BEFORE INSERT OR UPDATE
  ON messages FOR EACH ROW EXECUTE FUNCTION messages_tsv_trigger();

CREATE INDEX IF NOT EXISTS idx_messages_conv_time ON messages (conversation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_tsv ON messages USING GIN (content_tsv);

-- =====================
-- Knowledge Management
-- =====================
CREATE TABLE IF NOT EXISTS knowledge_entities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id VARCHAR(255),
  content TEXT NOT NULL,
  entity_type VARCHAR(100),
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  version INTEGER DEFAULT 1,
  embedding vector(1536),
  metadata JSONB
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_knowledge_external_id ON knowledge_entities(external_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_entity_type ON knowledge_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_entities USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);

CREATE TABLE IF NOT EXISTS knowledge_provenance (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id UUID REFERENCES knowledge_entities(id) ON DELETE CASCADE,
  source VARCHAR(255),
  evidence TEXT,
  actor UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB
);

CREATE TABLE IF NOT EXISTS knowledge_conflicts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id UUID REFERENCES knowledge_entities(id) ON DELETE CASCADE,
  field VARCHAR(100) NOT NULL,
  proposed_value JSONB NOT NULL,
  status VARCHAR(30) DEFAULT 'open',         -- open|resolved|dismissed
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  resolved_at TIMESTAMP,
  resolved_by UUID REFERENCES users(id),
  resolution_note TEXT
);

-- =====================
-- Workflows / Agents
-- =====================
CREATE TABLE IF NOT EXISTS workflows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) UNIQUE NOT NULL,
  definition JSONB NOT NULL,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
  status VARCHAR(30) DEFAULT 'pending',      -- pending|running|succeeded|failed|cancelled
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  finished_at TIMESTAMP,
  logs JSONB
);

-- =====================
-- Audit Log
-- =====================
CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGSERIAL PRIMARY KEY,
  occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  actor_id UUID REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  target_type VARCHAR(100),
  target_id UUID,
  details JSONB
);

-- Helpful views
CREATE OR REPLACE VIEW v_conversation_latest AS
SELECT c.id AS conversation_id,
       c.title,
       c.created_by,
       m.id AS last_message_id,
       m.content AS last_message,
       m.created_at AS last_message_at
FROM conversations c
LEFT JOIN LATERAL (
  SELECT * FROM messages m2 WHERE m2.conversation_id = c.id ORDER BY created_at DESC LIMIT 1
) m ON TRUE;
