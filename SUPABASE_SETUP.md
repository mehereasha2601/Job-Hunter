# Supabase Setup Guide

Follow these steps to set up your Supabase database for Phase 2.

---

## Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Sign up with GitHub or email
3. Create a new project:
   - Choose a name (e.g., "job-hunter")
   - Choose a database password (save this!)
   - Select region closest to you (US East for Boston)
   - Click "Create new project"
   - Wait ~2 minutes for provisioning

---

## Step 2: Run Database Schema

1. In Supabase dashboard, click "SQL Editor" in left sidebar
2. Click "New query"
3. Paste the SQL schema below
4. Click "Run" (bottom right)

```sql
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  title TEXT,
  company TEXT,
  url TEXT,
  source TEXT,  -- 'linkedin' | 'indeed' | 'greenhouse' | 'google' | 'ziprecruiter'
  description TEXT,
  location TEXT,
  date_posted TIMESTAMPTZ,  -- When the job was originally posted by company
  score REAL,
  h1b_flag TEXT,  -- 'confirmed' | 'unknown' | 'blocked'
  on_target_list BOOLEAN DEFAULT false,
  duplicate_of TEXT,  -- nullable, id of duplicate
  status TEXT DEFAULT 'seen',  -- seen | scored | tailored | applied | response | interview | offer | rejected
  first_seen_at TIMESTAMPTZ DEFAULT now(),
  tailored_at TIMESTAMPTZ,
  applied_at TIMESTAMPTZ,
  resume_pdf_url TEXT,
  doc_url TEXT,
  email_doc_url TEXT,
  md_path TEXT,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(score);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_first_seen ON jobs(first_seen_at);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON jobs(date_posted);
```

You should see: "Success. No rows returned"

---

## Step 3: Get API Credentials

1. In Supabase dashboard, click "Project Settings" (gear icon, bottom left)
2. Click "API" in the sidebar
3. Copy these two values:

   **Project URL:**
   ```
   https://xxxxxxxxxxxxx.supabase.co
   ```
   
   **anon/public key:**
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS...
   ```

---

## Step 4: Update .env File

1. Open your `.env` file (in the job-hunter root directory)
2. Add/update these lines:

```bash
# Phase 2 - Database
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Important:** Use the **anon/public key**, NOT the service_role key (service_role bypasses Row Level Security and should never be exposed)

---

## Step 5: Test Connection

Run this to verify your database connection works:

```bash
source venv/bin/activate
python -c "from src.db import Database; db = Database(); print('✓ Database connected successfully!')"
```

If you see "✓ Database connected successfully!", you're all set!

---

## Optional: Set Up Row Level Security (RLS)

For production use, enable RLS policies:

```sql
-- Enable RLS on jobs table
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for service role (for your pipeline)
CREATE POLICY "Service role has full access" 
ON jobs 
FOR ALL 
TO authenticated 
USING (true) 
WITH CHECK (true);

-- Policy: Allow read-only for anon (for your web UI)
CREATE POLICY "Public read access" 
ON jobs 
FOR SELECT 
TO anon 
USING (true);
```

**Note:** For Phase 2 testing, you can skip RLS. It's mainly for Phase 3 when the web UI is live.

---

## Troubleshooting

**Error: "Invalid API key"**
- Check that you copied the full key (it's very long)
- Make sure you used the anon key, not service_role

**Error: "Relation 'jobs' does not exist"**
- Go back to Step 2 and run the SQL schema
- Make sure it showed "Success" not an error

**Error: "Network error"**
- Check your internet connection
- Verify the SUPABASE_URL is correct (should end in .supabase.co)

---

## Next Steps After Setup

Once Supabase is configured:

1. **Test the scraper** (start with 1-2 Greenhouse boards)
2. **Test the scorer** on scraped jobs
3. **Test the tailor** with a job ID
4. Move to **Phase 3** (GitHub Actions + Web UI)
