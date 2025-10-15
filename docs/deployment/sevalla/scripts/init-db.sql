-- OBCMS Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time
-- It sets up the database with proper extensions and initial configurations

-- Create extensions that OBCMS needs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search and similarity
CREATE EXTENSION IF NOT EXISTS "unaccent";  -- For accent-insensitive search

-- Create custom functions if needed
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Set up timezone configuration
SET timezone = 'Asia/Manila';

-- Create indexes for common queries (these will be created by Django migrations too,
-- but having them here can improve initial setup performance)

-- Example indexes (commented out as Django will create these via migrations)
-- CREATE INDEX IF NOT EXISTS idx_common_user_email ON common_user(email);
-- CREATE INDEX IF NOT EXISTS idx_common_user_is_active ON common_user(is_active);
-- CREATE INDEX IF NOT EXISTS idx_communities_obccommunity_name_trgm ON communities_obccommunity USING gin(name gin_trgm_ops);

-- Grant necessary permissions
-- These are handled by Django's migration system

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'OBCMS database initialized successfully';
    RAISE NOTICE 'Extensions created: uuid-ossp, pg_trgm, unaccent';
    RAISE NOTICE 'Timezone set to: %', current_setting('timezone');
END $$;