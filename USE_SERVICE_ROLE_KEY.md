# Supabase 403 Error - Use Service Role Key

## The Problem
The anon key is being blocked by RLS even after disabling it. This can happen due to caching or policy conflicts.

## Solution: Use Service Role Key

### Step 1: Get Your Service Role Key

1. Go to **Supabase Dashboard** → **Settings** → **API**
2. Look for **Project API keys** section
3. You'll see TWO keys:
   - `anon` / `public` key (starts with `eyJhbGci...`)
   - `service_role` key (starts with `eyJhbGci...` but is different)

4. Copy the **service_role** key (NOT the anon key)

### Step 2: Update .env

Replace the current `SUPABASE_KEY` in your `.env` file with the service_role key:

```bash
# Change this line (line 28):
SUPABASE_KEY=eyJhbGci... (your NEW service_role key)
```

⚠️ **Important:** The service_role key is SECRET - never commit it to GitHub!

### Step 3: Restart the API

```bash
# Kill the old API process
lsof -ti:8000 | xargs kill -9

# Restart with new key
cd /Users/koppisettyeashameher/job-hunter
python3 api/main.py
```

### Step 4: Test Login

Refresh http://localhost:3001/ and login with `jobhunter2026`

## Why Service Role Key?

- **Anon key:** Subject to RLS policies (public-facing, safe for frontend)
- **Service role key:** Bypasses ALL RLS policies (backend/API use, full access)

Since your API is password-protected and runs on localhost (not public), using the service_role key is safe and will solve the 403 issue immediately.

## Verification

After updating the key and restarting, test:
```bash
curl http://localhost:8000/api/health
```

Should work without 403 errors!
