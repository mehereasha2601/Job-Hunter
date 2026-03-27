-- Comprehensive Supabase Diagnostics & Fix
-- Run ALL of these queries in Supabase SQL Editor

-- 1. Check if jobs table exists
SELECT 'Table exists: ' || CASE WHEN EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'jobs'
) THEN 'YES' ELSE 'NO' END as result;

-- 2. Check RLS status
SELECT 
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables
WHERE tablename = 'jobs' AND schemaname = 'public';

-- 3. Check existing policies
SELECT policyname, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'jobs';

-- 4. DISABLE RLS (force it)
ALTER TABLE public.jobs DISABLE ROW LEVEL SECURITY;

-- 5. Drop all policies (they might be interfering)
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'jobs') LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON jobs';
    END LOOP;
END $$;

-- 6. Verify RLS is now disabled
SELECT 
  'RLS Status: ' || CASE WHEN rowsecurity THEN 'ENABLED (problem!)' ELSE 'DISABLED (good!)' END as status
FROM pg_tables
WHERE tablename = 'jobs' AND schemaname = 'public';

-- 7. Test a simple query
SELECT COUNT(*) as total_jobs FROM jobs;

-- 8. Check date_posted column exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'jobs' AND column_name = 'date_posted';

-- Expected output:
-- Table exists: YES
-- rls_enabled: false
-- RLS Status: DISABLED (good!)
-- total_jobs: (some number)
-- date_posted | timestamp with time zone
