-- Check if RLS is enabled on jobs table
-- Run this in Supabase SQL Editor

SELECT 
  schemaname,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables
WHERE tablename = 'jobs';

-- This should show rls_enabled = false if you disabled it
-- If it shows true, RLS is still enabled

-- To disable RLS (run if rls_enabled = true):
ALTER TABLE jobs DISABLE ROW LEVEL SECURITY;

-- Verify it's disabled:
SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'jobs';
