-- Brand profiles table for style-management CRUD
CREATE TABLE IF NOT EXISTS brand_profiles (
  id UUID PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  guidelines JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Keep updated_at in sync
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_brand_profiles_updated_at ON brand_profiles;
CREATE TRIGGER trg_brand_profiles_updated_at
BEFORE UPDATE ON brand_profiles
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
