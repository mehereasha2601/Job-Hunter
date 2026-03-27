-- Migration: Add date_posted column to jobs table
-- Run this in Supabase SQL Editor

-- Add date_posted column (nullable for existing records)
ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS date_posted TIMESTAMPTZ;

-- Add index for date_posted (useful for sorting by recency)
CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON jobs(date_posted);

-- Update existing jobs to set date_posted = first_seen_at (best estimate)
UPDATE jobs 
SET date_posted = first_seen_at 
WHERE date_posted IS NULL AND first_seen_at IS NOT NULL;

-- Verify migration
SELECT 
  COUNT(*) as total_jobs,
  COUNT(date_posted) as jobs_with_date,
  MIN(date_posted) as oldest_posted,
  MAX(date_posted) as newest_posted
FROM jobs;
