-- Enhanced AI Agent OS - PostgreSQL Extensions Initialization
-- Connect to the main database
\c enhanced_ai_os;

-- Enable commonly used extensions (idempotent)
-- plpgsql is usually present; keeping it simple
CREATE EXTENSION IF NOT EXISTS plpgsql;

-- Helper DO wrapper to ignore missing extensions
DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS pgcrypto';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'pgcrypto extension not found; skipping'; END;
END $$;

-- Query performance tracking
DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS pg_stat_statements';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'pg_stat_statements extension not found; ensure shared_preload_libraries is set; skipping'; END;
END $$;

DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'uuid-ossp extension not found; skipping'; END;
END $$;

DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS hstore';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'hstore extension not found; skipping'; END;
END $$;

DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS ltree';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'ltree extension not found; skipping'; END;
END $$;

DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS pg_trgm';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'pg_trgm extension not found; skipping'; END;
END $$;

DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS btree_gin';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'btree_gin extension not found; skipping'; END;
END $$;

DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS btree_gist';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'btree_gist extension not found; skipping'; END;
END $$;

DO $$ BEGIN
  BEGIN EXECUTE 'CREATE EXTENSION IF NOT EXISTS vector';
  EXCEPTION WHEN undefined_file THEN RAISE NOTICE 'vector extension not found; skipping'; END;
END $$;

-- TimescaleDB (optional, requires image with extension preloaded)
-- Will succeed only if extension is available in the Postgres image
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb') THEN
        EXECUTE 'CREATE EXTENSION IF NOT EXISTS timescaledb';
    ELSE
        RAISE NOTICE 'timescaledb extension not found in pg_available_extensions; skipping';
    END IF;
END
$$;
