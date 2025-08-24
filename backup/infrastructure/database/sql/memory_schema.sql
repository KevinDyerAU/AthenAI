-- Conversation memory persistence schema
-- Stores per-session memory keys and context payloads for orchestration

CREATE TABLE IF NOT EXISTS conversations_memory (
  session_id TEXT PRIMARY KEY,
  user_id TEXT,
  keys JSONB DEFAULT '[]'::jsonb,
  context JSONB DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Helpful index for user queries
CREATE INDEX IF NOT EXISTS conversations_memory_user_id_idx ON conversations_memory (user_id);
