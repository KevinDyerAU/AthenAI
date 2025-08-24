-- Enhanced AI Agent OS - PostgreSQL Database Initialization
-- This script creates the necessary databases and basic structure

-- Create main application database (if not exists from environment)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'enhanced_ai_os') THEN
        CREATE DATABASE enhanced_ai_os;
    END IF;
END
$$;

-- Connect to the main database for further setup
\c enhanced_ai_os;

-- Create schemas for different components
CREATE SCHEMA IF NOT EXISTS n8n;
CREATE SCHEMA IF NOT EXISTS ai_agents;
CREATE SCHEMA IF NOT EXISTS consciousness;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create application user with appropriate permissions
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ai_agent_user') THEN
        CREATE ROLE ai_agent_user WITH LOGIN PASSWORD 'secure_password_change_me';
    END IF;
END
$$;

-- Grant permissions to application user
GRANT CONNECT ON DATABASE enhanced_ai_os TO ai_agent_user;
GRANT USAGE ON SCHEMA n8n TO ai_agent_user;
GRANT USAGE ON SCHEMA ai_agents TO ai_agent_user;
GRANT USAGE ON SCHEMA consciousness TO ai_agent_user;
GRANT USAGE ON SCHEMA monitoring TO ai_agent_user;
GRANT USAGE ON SCHEMA audit TO ai_agent_user;

-- Grant table creation permissions
GRANT CREATE ON SCHEMA n8n TO ai_agent_user;
GRANT CREATE ON SCHEMA ai_agents TO ai_agent_user;
GRANT CREATE ON SCHEMA consciousness TO ai_agent_user;
GRANT CREATE ON SCHEMA monitoring TO ai_agent_user;
GRANT CREATE ON SCHEMA audit TO ai_agent_user;

-- Create audit logging function
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit.change_log (
            table_name, operation, old_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME, TG_OP, row_to_json(OLD), current_user, now()
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.change_log (
            table_name, operation, old_values, new_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), current_user, now()
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit.change_log (
            table_name, operation, new_values, changed_by, changed_at
        ) VALUES (
            TG_TABLE_NAME, TG_OP, row_to_json(NEW), current_user, now()
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION audit.log_changes() IS 'Audit trigger function for tracking data changes';
