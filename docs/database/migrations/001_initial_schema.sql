-- Migration: 001_initial_schema
-- Description: Initial database schema for TikTok AI Automation
-- Author: Constitutional AI System
-- Date: 2025-01-28

BEGIN;

-- Check if migration was already applied
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'schema_migrations') THEN
        IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '001') THEN
            RAISE EXCEPTION 'Migration 001 already applied';
        END IF;
    END IF;
END $$;

-- Create migrations tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(10) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Apply the main schema
\i ../schema.sql

-- Record migration
INSERT INTO schema_migrations (version) VALUES ('001');

-- Verify critical indexes exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_content_sources_discovered') THEN
        RAISE EXCEPTION 'Critical index idx_content_sources_discovered missing';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_videos_status') THEN
        RAISE EXCEPTION 'Critical index idx_videos_status missing';
    END IF;
END $$;

COMMIT;