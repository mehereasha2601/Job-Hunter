# GitHub Secrets Setup Guide

This guide shows how to configure GitHub repository secrets for the automated pipeline.

---

## What Are GitHub Secrets?

GitHub Secrets are encrypted environment variables that GitHub Actions workflows can access. They keep your API keys secure and out of the codebase.

---

## Step 1: Navigate to Secrets

1. Go to your GitHub repository
2. Click "Settings" (top navigation)
3. In left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret" for each secret below

---

## Step 2: Add Required Secrets

### For Phase 2 & 3 (Minimum Required):

| Secret Name | Value | Where to Get It |
|-------------|-------|-----------------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase Project Settings → API |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIs...` | Supabase Project Settings → API (anon/public key) |
| `GROQ_API_KEY` | `gsk_...` | https://console.groq.com/keys |
| `GEMINI_API_KEY` | `AIza...` | https://aistudio.google.com/apikey |
| `NOTIFICATION_EMAIL` | `your_email@gmail.com` | Your Gmail address |

### Optional (For Full Features):

| Secret Name | Value | Where to Get It |
|-------------|-------|-----------------|
| `GMAIL_APP_PASSWORD` | `xxxx xxxx xxxx xxxx` | https://myaccount.google.com/apppasswords |
| `APIFY_TOKEN` | `apify_api_...` | https://console.apify.com/account/integrations |
| `GOOGLE_CREDENTIALS_JSON` | `{"type":"service_account",...}` | Google Cloud Console → Service Accounts |
| `GH_PAT` | `ghp_...` | GitHub Settings → Developer Settings → Personal Access Tokens |
| `UI_PASSWORD` | `your_password` | Choose a password for web UI |

---

## Step 3: How to Add Each Secret

### Example: Adding SUPABASE_URL

1. Click "New repository secret"
2. Name: `SUPABASE_URL`
3. Secret: Paste your Supabase URL (e.g., `https://abcdefghij.supabase.co`)
4. Click "Add secret"

Repeat for each secret in the tables above.

---

## Detailed Instructions for Each Secret

### GROQ_API_KEY
1. Go to https://console.groq.com
2. Sign in
3. Click "API Keys" in left sidebar
4. Click "Create API Key"
5. Copy the key (starts with `gsk_`)
6. Add as GitHub secret

### GEMINI_API_KEY
1. Go to https://aistudio.google.com
2. Sign in with Google
3. Click "Get API key"
4. Create API key
5. Copy the key (starts with `AIza`)
6. Add as GitHub secret

### GMAIL_APP_PASSWORD
1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Gmail
3. Create new app password
   - Name it "Job Hunter Pipeline"
4. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
5. Add as GitHub secret
   
**Note:** This is NOT your regular Gmail password. It's a special app-specific password.

### GOOGLE_CREDENTIALS_JSON
1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Enable Google Docs API and Google Drive API
4. Go to "IAM & Admin" → "Service Accounts"
5. Create service account
6. Click on the account → "Keys" tab → "Add Key" → "Create new key" → JSON
7. Download the JSON file
8. Copy the ENTIRE JSON content (it's one long line)
9. Add as GitHub secret

### GH_PAT (GitHub Personal Access Token)
1. GitHub Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens
2. Click "Generate new token"
3. Name: "Job Hunter Pipeline"
4. Expiration: 90 days (or longer)
5. Permissions needed:
   - Repository access: Select your job-hunter repo
   - Permissions: `actions` (read/write), `contents` (read/write)
6. Generate token
7. Copy token (starts with `github_pat_` or `ghp_`)
8. Add as GitHub secret

---

## Step 4: Verify Secrets

After adding all secrets:

1. Go to repository Settings → Secrets → Actions
2. You should see all secrets listed (values are hidden)
3. Count: Should have 5-10 secrets depending on optional features

---

## Which Secrets Are Mandatory?

### To Run Scraping & Scoring (Phase 3 minimum):
- ✅ Required: `SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`
- ⚠️ Optional: `NOTIFICATION_EMAIL` (you won't get digest emails without this)

### To Get Email Notifications:
- ✅ Required: `NOTIFICATION_EMAIL`, `GMAIL_APP_PASSWORD`

### To Create Google Docs:
- ✅ Required: `GOOGLE_CREDENTIALS_JSON`

### For Web UI (Phase 4):
- ✅ Required: `GH_PAT`, `UI_PASSWORD`

---

## Testing Secrets

After adding secrets, test by manually triggering a workflow:

1. Go to "Actions" tab in your repo
2. Click on "Step 1 - Score Jobs & Send Digest"
3. Click "Run workflow" → "Run workflow"
4. Wait 2-3 minutes
5. Check if it runs successfully

If it fails:
- Click on the failed run
- Check the logs for error messages
- Usually means a secret is missing or incorrect

---

## Security Notes

### DO:
- ✅ Use the anon/public key for Supabase (not service_role)
- ✅ Use Gmail app password (not your real password)
- ✅ Set PAT to expire after 90 days
- ✅ Keep secrets in GitHub only (never commit to code)

### DON'T:
- ❌ Never commit `.env` file (it's in `.gitignore`)
- ❌ Never use Supabase service_role key (bypass security)
- ❌ Never share your API keys publicly
- ❌ Never screenshot secrets

---

## Quick Reference: All Secrets

```bash
# Phase 2 & 3 - Required
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...
NOTIFICATION_EMAIL=your@gmail.com

# Phase 2 & 3 - Optional
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
APIFY_TOKEN=apify_api_...
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# Phase 4 - Web UI
GH_PAT=github_pat_... or ghp_...
UI_PASSWORD=your_chosen_password
```

---

## Troubleshooting

**Error: "Secret not found"**
- Check spelling (must match exactly)
- Secrets are case-sensitive
- Re-add the secret

**Error: "Invalid credentials"**
- Check the value is correct
- Make sure you copied the full key (some are very long)
- No extra spaces before/after the value

**Error: "Permission denied"**
- For GH_PAT: Check token has `actions` and `contents` permissions
- For Google: Check service account has Docs/Drive API enabled

---

## Next Steps

After adding secrets:
1. Commit and push your `.github/workflows/` folder
2. Go to Actions tab
3. Manually trigger one workflow to test
4. If successful, all automated runs will work

See `PHASE3_COMPLETE.md` for full deployment instructions.
