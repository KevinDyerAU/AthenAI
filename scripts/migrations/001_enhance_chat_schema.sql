
ALTER TABLE chat_sessions 
ADD COLUMN IF NOT EXISTS message TEXT,
ADD COLUMN IF NOT EXISTS context JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS message_count INTEGER DEFAULT 0;

CREATE TABLE IF NOT EXISTS chat_responses (
  id BIGSERIAL PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
  user_id TEXT,
  response TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS chat_responses_session_created_idx ON chat_responses (session_id, created_at);
