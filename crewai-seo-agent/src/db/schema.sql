-- Drop existing tables if they exist
DROP TABLE IF EXISTS seo_jobs;

-- Create single consolidated table
CREATE TABLE IF NOT EXISTS seo_jobs (
    id SERIAL PRIMARY KEY,
    website_url TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error TEXT,
    final_answer JSONB DEFAULT '{}'::jsonb
);

-- Create indices if they don't exist
CREATE INDEX IF NOT EXISTS idx_seo_jobs_status ON seo_jobs(status);
CREATE INDEX IF NOT EXISTS idx_seo_jobs_website_url ON seo_jobs(website_url);

-- Update final_answer column to be of type jsonb
ALTER TABLE seo_jobs 
ALTER COLUMN final_answer TYPE jsonb USING final_answer::jsonb;