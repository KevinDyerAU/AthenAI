-- Enhanced AI Agent OS - PostgreSQL Extensions Initialization
-- Connect to the main database
\c enhanced_ai_os;

-- Enable commonly used extensions (idempotent)
CREATE EXTENSION IF NOT EXISTS plpgsql;           -- Usually installed by default
CREATE EXTENSION IF NOT EXISTS pgcrypto;          -- gen_random_uuid(), cryptographic functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";       -- uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS hstore;            -- key/value store
CREATE EXTENSION IF NOT EXISTS ltree;             -- tree-like label paths
CREATE EXTENSION IF NOT EXISTS pg_trgm;           -- trigram search
CREATE EXTENSION IF NOT EXISTS btree_gin;         -- btree emulation for GIN
CREATE EXTENSION IF NOT EXISTS btree_gist;        -- btree emulation for GiST
CREATE EXTENSION IF NOT EXISTS vector;            -- pgvector for embeddings

-- TimescaleDB (optional, requires image with extension preloaded)
-- Will succeed only if extension is available in the Postgres image
DO $$
BEGIN
    BEGIN
        EXECUTE 'CREATE EXTENSION IF NOT EXISTS timescaledb';
    EXCEPTION WHEN undefined_file THEN
        -- Extension not available in the image; proceed without failing init
        RAISE NOTICE 'timescaledb extension not found; skipping';
    END;
END
$$;
