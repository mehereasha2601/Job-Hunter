# UI Login Issue - 403 Forbidden

## Problem
UI password is correct (`jobhunter2026`) but getting 403 Forbidden error when accessing the API.

## Root Cause
Supabase Row Level Security (RLS) is likely blocking access because the anon key doesn't have proper policies.

## Quick Fix

### Option 1: Disable RLS (Fastest - for development)

In Supabase SQL Editor:
```sql
ALTER TABLE jobs DISABLE ROW LEVEL SECURITY;
```

Then refresh the UI at: http://localhost:3001/

### Option 2: Fix RLS Policies (Better - for production)

In Supabase SQL Editor, run `migrations/fix_rls_policies.sql`:
```sql
-- Enable RLS
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Allow all access for anon role (API uses anon key)
CREATE POLICY "Enable all access for anon"
ON jobs FOR ALL TO anon
USING (true) WITH CHECK (true);
```

Then refresh the UI.

## Verification

After applying the fix, test the API:
```bash
curl -u "user:jobhunter2026" http://localhost:8000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-03-26T..."
}
```

## Understanding the Issue

**What happened:**
1. Your `.env` has `UI_PASSWORD=jobhunter2026` ✅ Correct
2. FastAPI authentication works ✅ Password verified
3. Supabase connection attempted ❌ RLS blocks anon key

**Why:**
- Your API uses the Supabase **anon key** (from `SUPABASE_KEY`)
- RLS is enabled on the `jobs` table
- No policy exists allowing anon role to read/write

**Solution:**
- Either disable RLS for development
- Or create a policy allowing anon role full access

## After Fixing

1. Refresh browser: http://localhost:3001/
2. Login with password: `jobhunter2026`
3. You should see the jobs table with:
   - Score column
   - Company, Role, Location
   - **Posted column** (NEW - showing "5h ago", etc.)
   - **Sort By dropdown** (NEW - Score, Date Posted, Recently Added)
   - Status dropdown
   - Action buttons

## Recommended: Disable RLS for Now

Since this is a development/personal project, the simplest approach is:
```sql
ALTER TABLE jobs DISABLE ROW LEVEL SECURITY;
```

You can re-enable it later if you deploy publicly.
