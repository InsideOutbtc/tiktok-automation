-- TikTok AI Automation Database Schema
-- Optimized for <5ms queries with Constitutional AI principles

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Custom types
CREATE TYPE content_status AS ENUM ('discovered', 'processing', 'processed', 'published', 'failed');
CREATE TYPE agent_type AS ENUM ('viral_scout', 'clip_selector', 'hook_writer', 'engagement_predictor');
CREATE TYPE error_tier AS ENUM ('tier1', 'tier2', 'tier3', 'tier4');
CREATE TYPE platform AS ENUM ('tiktok', 'youtube', 'instagram', 'twitter');

-- Partitioned tables for scale
CREATE TABLE content_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform platform NOT NULL,
    source_id VARCHAR(255) NOT NULL,
    source_url TEXT NOT NULL,
    author_handle VARCHAR(255),
    author_id VARCHAR(255),
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    viral_score DECIMAL(5,2),
    processed BOOLEAN DEFAULT FALSE,
    UNIQUE(platform, source_id)
) PARTITION BY RANGE (discovered_at);

-- Create monthly partitions
CREATE TABLE content_sources_2025_01 PARTITION OF content_sources
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE content_sources_2025_02 PARTITION OF content_sources
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Indexes for <5ms queries
CREATE INDEX idx_content_sources_discovered ON content_sources(discovered_at DESC);
CREATE INDEX idx_content_sources_platform_processed ON content_sources(platform, processed);
CREATE INDEX idx_content_sources_viral_score ON content_sources(viral_score DESC) WHERE viral_score IS NOT NULL;
CREATE INDEX idx_content_sources_metadata ON content_sources USING gin(metadata);

-- Video processing table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES content_sources(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    resolution VARCHAR(20),
    fps INTEGER,
    size_bytes BIGINT,
    status content_status DEFAULT 'discovered',
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    error_tier error_tier,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_source ON videos(source_id);
CREATE INDEX idx_videos_processing ON videos(processing_started_at) WHERE status = 'processing';

-- Generated clips
CREATE TABLE clips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    start_time DECIMAL(10,3) NOT NULL,
    end_time DECIMAL(10,3) NOT NULL,
    duration DECIMAL(10,3) GENERATED ALWAYS AS (end_time - start_time) STORED,
    file_path TEXT,
    thumbnail_path TEXT,
    viral_potential_score DECIMAL(5,2),
    hook_score DECIMAL(5,2),
    retention_score DECIMAL(5,2),
    effects_applied JSONB DEFAULT '[]',
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clips_video ON clips(video_id);
CREATE INDEX idx_clips_scores ON clips(viral_potential_score DESC, hook_score DESC);
CREATE INDEX idx_clips_published ON clips(published, created_at DESC);

-- AI agent decisions
CREATE TABLE agent_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type agent_type NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,
    decision JSONB NOT NULL,
    confidence DECIMAL(3,2),
    reasoning TEXT,
    patterns_used JSONB DEFAULT '[]',
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_decisions_target ON agent_decisions(target_type, target_id);
CREATE INDEX idx_agent_decisions_agent ON agent_decisions(agent_type, created_at DESC);
CREATE INDEX idx_agent_decisions_patterns ON agent_decisions USING gin(patterns_used);

-- Pattern storage for PIECES integration
CREATE TABLE learned_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type VARCHAR(100) NOT NULL,
    pattern_data JSONB NOT NULL,
    success_rate DECIMAL(5,2),
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patterns_type_success ON learned_patterns(pattern_type, success_rate DESC);
CREATE INDEX idx_patterns_usage ON learned_patterns(usage_count DESC);
CREATE INDEX idx_patterns_data ON learned_patterns USING gin(pattern_data);

-- Publishing records
CREATE TABLE publications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clip_id UUID REFERENCES clips(id) ON DELETE CASCADE,
    platform platform NOT NULL,
    platform_post_id VARCHAR(255),
    title TEXT,
    description TEXT,
    hashtags TEXT[],
    published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN views > 0 THEN ((likes + comments + shares)::DECIMAL / views * 100) ELSE 0 END
    ) STORED,
    last_stats_update TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_publications_clip ON publications(clip_id);
CREATE INDEX idx_publications_platform ON publications(platform, published_at DESC);
CREATE INDEX idx_publications_engagement ON publications(engagement_rate DESC);

-- Error tracking for Constitutional AI
CREATE TABLE error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    error_tier error_tier NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT,
    stack_trace TEXT,
    context JSONB DEFAULT '{}',
    auto_recovered BOOLEAN DEFAULT FALSE,
    recovery_action TEXT,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_errors_service_tier ON error_logs(service_name, error_tier, occurred_at DESC);
CREATE INDEX idx_errors_auto_recovered ON error_logs(auto_recovered, occurred_at DESC);

-- Performance metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(100) NOT NULL,
    service_name VARCHAR(100),
    value DECIMAL(10,3) NOT NULL,
    unit VARCHAR(20),
    tags JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_type_time ON performance_metrics(metric_type, recorded_at DESC);
CREATE INDEX idx_metrics_service ON performance_metrics(service_name, recorded_at DESC);

-- Materialized view for dashboard
CREATE MATERIALIZED VIEW dashboard_stats AS
SELECT 
    COUNT(DISTINCT cs.id) as total_sources,
    COUNT(DISTINCT v.id) as total_videos,
    COUNT(DISTINCT c.id) as total_clips,
    COUNT(DISTINCT p.id) as total_publications,
    AVG(c.viral_potential_score) as avg_viral_score,
    AVG(p.engagement_rate) as avg_engagement_rate,
    COUNT(DISTINCT CASE WHEN v.status = 'processing' THEN v.id END) as videos_processing,
    COUNT(DISTINCT CASE WHEN el.occurred_at > NOW() - INTERVAL '1 hour' THEN el.id END) as recent_errors
FROM content_sources cs
LEFT JOIN videos v ON cs.id = v.source_id
LEFT JOIN clips c ON v.id = c.video_id
LEFT JOIN publications p ON c.id = p.clip_id
LEFT JOIN error_logs el ON el.occurred_at > NOW() - INTERVAL '24 hours';

CREATE UNIQUE INDEX idx_dashboard_stats ON dashboard_stats(total_sources);

-- Functions for atomic operations
CREATE OR REPLACE FUNCTION update_video_status(
    p_video_id UUID,
    p_status content_status,
    p_error_message TEXT DEFAULT NULL,
    p_error_tier error_tier DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE videos 
    SET 
        status = p_status,
        error_message = p_error_message,
        error_tier = p_error_tier,
        processing_completed_at = CASE 
            WHEN p_status IN ('processed', 'failed') THEN CURRENT_TIMESTAMP 
            ELSE processing_completed_at 
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_video_id;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patterns_updated_at BEFORE UPDATE ON learned_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Optimize for concurrent writes
ALTER TABLE content_sources SET (fillfactor = 90);
ALTER TABLE videos SET (fillfactor = 90);
ALTER TABLE clips SET (fillfactor = 90);
ALTER TABLE agent_decisions SET (fillfactor = 95);

-- Performance configuration
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;