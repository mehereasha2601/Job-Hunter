-- Fix RLS Policies for API Access
-- Run this in Supabase SQL Editor if you're getting 403 errors

-- Option 1: Disable RLS (for development/testing)
ALTER TABLE jobs DISABLE ROW LEVEL SECURITY;

-- Option 2: Enable proper policies (for production)
-- First, enable RLS
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Service role has full access" ON jobs;
DROP POLICY IF EXISTS "Public read access" ON jobs;
DROP POLICY IF EXISTS "Enable all access for anon" ON jobs;

-- Policy: Allow all operations for anon role (your API uses anon key)
CREATE POLICY "Enable all access for anon"
ON jobs
FOR ALL
TO anon
USING (true)
WITH CHECK (true);

-- Policy: Allow all operations for authenticated users
CREATE POLICY "Enable all access for authenticated"
ON jobs
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- Verify policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE tablename = 'jobs';
