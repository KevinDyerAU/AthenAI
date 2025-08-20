-- Enhanced AI Agent OS - PostgreSQL Schemas, Tables, Indexes, Triggers, Seed
-- Connect to the main database
\c enhanced_ai_os;

-- =====================================================================
-- Audit Schema Objects
-- =====================================================================
CREATE TABLE IF NOT EXISTS audit.change_log (
    id           bigserial PRIMARY KEY,
    table_name   text        NOT NULL,
    operation    text        NOT NULL,
    old_values   jsonb,
    new_values   jsonb,
    changed_by   text        NOT NULL DEFAULT current_user,
    changed_at   timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE audit.change_log IS 'Central audit trail for DML operations';

-- =====================================================================
-- Core Domain Schemas / Tables
-- =====================================================================
-- Agents
CREATE TABLE IF NOT EXISTS ai_agents.agents (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name         text        NOT NULL UNIQUE,
    description  text,
    status       text        NOT NULL DEFAULT 'active',
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

-- Knowledge base items associated to an agent
CREATE TABLE IF NOT EXISTS ai_agents.knowledge_base (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id     uuid        NOT NULL REFERENCES ai_agents.agents(id) ON DELETE CASCADE,
    title        text        NOT NULL,
    content      text        NOT NULL,
    tags         text[]      DEFAULT '{}',
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

-- Embeddings for arbitrary resources
CREATE TABLE IF NOT EXISTS ai_agents.embeddings (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type  text        NOT NULL,
    resource_id    uuid        NOT NULL,
    embedding      vector(1536) NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now()
);

-- Memories / consciousness entries
CREATE TABLE IF NOT EXISTS consciousness.memories (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id     uuid        NOT NULL REFERENCES ai_agents.agents(id) ON DELETE CASCADE,
    content      text        NOT NULL,
    metadata     jsonb       NOT NULL DEFAULT '{}',
    salience     real        NOT NULL DEFAULT 0.0,
    embedding    vector(1536),
    created_at   timestamptz NOT NULL DEFAULT now()
);

-- Monitoring events (optionally hypertable if timescaledb exists)
CREATE TABLE IF NOT EXISTS monitoring.events (
    time      timestamptz NOT NULL DEFAULT now(),
    level     text        NOT NULL DEFAULT 'info',
    source    text        NOT NULL,
    message   text        NOT NULL,
    context   jsonb       NOT NULL DEFAULT '{}'
);

-- Try to convert monitoring.events to a hypertable if TimescaleDB is available
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'
    ) THEN
        PERFORM create_hypertable('monitoring.events', 'time', if_not_exists => TRUE);
    END IF;
END
$$;

-- =====================================================================
-- Indexes
-- =====================================================================
-- General purpose indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_base_agent ON ai_agents.knowledge_base(agent_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_resource ON ai_agents.embeddings(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_memories_agent_created ON consciousness.memories(agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_monitoring_time ON monitoring.events(time DESC);

-- Vector indexes (require pgvector)
-- IVF_FLAT typically benefits from a "lists" parameter; adjust via env if needed
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'vector'
    ) THEN
        -- Embeddings
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_embeddings_embedding ON ai_agents.embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)';
        -- Memories
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_memories_embedding ON consciousness.memories USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)';
    END IF;
END
$$;

-- Trigram for fuzzy search on titles/content
CREATE INDEX IF NOT EXISTS idx_kb_title_trgm ON ai_agents.knowledge_base USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_kb_content_trgm ON ai_agents.knowledge_base USING gin (content gin_trgm_ops);

-- =====================================================================
-- Triggers: Updated timestamps and Audit
-- =====================================================================
-- Updated timestamp triggers
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger
DROP TRIGGER IF EXISTS set_updated_at_agents ON ai_agents.agents;
CREATE TRIGGER set_updated_at_agents
BEFORE UPDATE ON ai_agents.agents
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_kb ON ai_agents.knowledge_base;
CREATE TRIGGER set_updated_at_kb
BEFORE UPDATE ON ai_agents.knowledge_base
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Audit triggers
DROP TRIGGER IF EXISTS audit_agents ON ai_agents.agents;
CREATE TRIGGER audit_agents
AFTER INSERT OR UPDATE OR DELETE ON ai_agents.agents
FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

DROP TRIGGER IF EXISTS audit_kb ON ai_agents.knowledge_base;
CREATE TRIGGER audit_kb
AFTER INSERT OR UPDATE OR DELETE ON ai_agents.knowledge_base
FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

DROP TRIGGER IF EXISTS audit_memories ON consciousness.memories;
CREATE TRIGGER audit_memories
AFTER INSERT OR UPDATE OR DELETE ON consciousness.memories
FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

-- =====================================================================
-- Privileges
-- =====================================================================
GRANT USAGE ON SCHEMA ai_agents, consciousness, monitoring, audit TO ai_agent_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ai_agents TO ai_agent_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA consciousness TO ai_agent_user;
GRANT SELECT ON ALL TABLES IN SCHEMA monitoring TO ai_agent_user;
GRANT SELECT, INSERT ON TABLE audit.change_log TO ai_agent_user;

-- Ensure future tables inherit the same privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_agents GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ai_agent_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA consciousness GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ai_agent_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA monitoring GRANT SELECT ON TABLES TO ai_agent_user;

-- =====================================================================
-- Seed Data (minimal)
-- =====================================================================
INSERT INTO ai_agents.agents (name, description)
VALUES ('default-agent', 'Default agent created during initialization')
ON CONFLICT (name) DO NOTHING;
