# Phase 3: GitHub Actions - COMPLETE ✅

**Date:** March 26, 2026  
**Status:** All workflows built and ready to deploy

---

## What Was Built

### 5 GitHub Actions Workflows

| Workflow | File | Schedule | Purpose |
|----------|------|----------|---------|
| 1️⃣ Greenhouse Scraper | `scrape_greenhouse.yml` | Every 30 min (9am-6pm) | Scrape 40 company boards |
| 2️⃣ JobSpy Scraper | `scrape_jobspy.yml` | Every 2 hours (9am-6pm) | LinkedIn/Indeed/Zip |
| 3️⃣ Apify Scraper | `scrape_apify.yml` | Every 2 hours (9am-6pm) | Google Jobs |
| 4️⃣ Step 1 Scoring | `step1_score.yml` | 3x/day (noon, 3pm, 6pm) | Score + digest email |
| 5️⃣ Step 2 Tailoring | `step2_tailor.yml` | On-demand | Generate outputs |

### Additional Components

- ✅ Cover letter generator (`src/cover_letter.py`)
- ✅ GitHub Secrets setup guide (`GITHUB_SECRETS_SETUP.md`)
- ✅ Cover letter integration in Step 2 pipeline
- ✅ Markdown output updated to include cover letters

---

## Complete Daily Schedule

### Weekdays (Mon-Fri), 9 AM - 6 PM EST

**Morning (9 AM - Noon):**
```
9:00 AM  → Greenhouse scrape #1
9:00 AM  → JobSpy scrape #1
9:00 AM  → Apify scrape #1
9:30 AM  → Greenhouse scrape #2
10:00 AM → Greenhouse scrape #3
10:30 AM → Greenhouse scrape #4
11:00 AM → Greenhouse scrape #5
11:00 AM → JobSpy scrape #2
11:00 AM → Apify scrape #2
11:30 AM → Greenhouse scrape #6

NOON     → ⭐ STEP 1: Score all new jobs + Digest Email #1
```

**Afternoon (Noon - 3 PM):**
```
12:30 PM → Greenhouse scrape #7
1:00 PM  → Greenhouse scrape #8
1:00 PM  → JobSpy scrape #3
1:00 PM  → Apify scrape #3
1:30 PM  → Greenhouse scrape #9
2:00 PM  → Greenhouse scrape #10
2:30 PM  → Greenhouse scrape #11

3:00 PM  → ⭐ STEP 1: Score all new jobs + Digest Email #2
```

**Evening (3 PM - 6 PM):**
```
3:00 PM  → Greenhouse scrape #12
3:00 PM  → JobSpy scrape #4
3:00 PM  → Apify scrape #4
3:30 PM  → Greenhouse scrape #13
4:00 PM  → Greenhouse scrape #14
4:30 PM  → Greenhouse scrape #15
5:00 PM  → Greenhouse scrape #16
5:00 PM  → JobSpy scrape #5
5:00 PM  → Apify scrape #5
5:30 PM  → Greenhouse scrape #17

6:00 PM  → ⭐ STEP 1: Score all new jobs + Digest Email #3
6:00 PM  → Greenhouse scrape #18
```

**Your Experience:**
- 📧 Get 3 digest emails per day (noon, 3pm, 6pm)
- ✅ Each email shows jobs scored 7.0+ with full details
- 🎯 Click to select jobs → Trigger Step 2 via UI or command

---

## How the Workflows Work

### Scraping Workflows (3 workflows)

**What they do:**
1. Run on cron schedule
2. Scrape jobs from their respective sources
3. Run H1B filter on each job
4. Store new jobs to Supabase (status='seen')
5. Skip duplicates automatically

**Outputs:**
- New jobs added to database
- Ready for scoring

### Step 1 - Scoring Workflow

**What it does:**
1. Runs 3x/day (noon, 3pm, 6pm)
2. Fetches all unscored jobs (status='seen')
3. LLM scores each job 1-10 based on 4 criteria
4. Updates database with scores (status='scored')
5. Sends digest email with jobs scoring 7.0+

**Your digest email includes:**
- Score (out of 10)
- Job title, company, location
- First 500 chars of JD
- Tech stack extracted
- Link to job posting
- H1B status (✅ confirmed / ⚠️ unknown)

### Step 2 - Tailoring Workflow

**What it does:**
1. Triggered manually with job IDs
2. Generates tailored resume for each job
3. Drafts 2 cold email versions
4. Generates cover letter (if JD requires it)
5. Runs all 4 guardrails
6. Creates Google Docs
7. Saves markdown backup
8. Commits to repo
9. Sends completion email with doc links

**Trigger methods:**
- Via web UI (Phase 4)
- Via GitHub Actions UI (manual run)
- Via `gh` CLI: `gh workflow run step2_tailor.yml -f job_ids="id1,id2,id3"`

---

## GitHub Actions Billing

### Free Tier Limits
- **2,000 minutes/month** for public repos
- **500 MB storage** for artifacts

### Your Usage (Section 2 of spec)
- Greenhouse: 18 runs/day × 1 min × 22 days = 396 min
- JobSpy + Apify: 10 runs/day × 2 min × 22 days = 440 min
- Step 1: 3 runs/day × 3 min × 22 days = 198 min
- Step 2: 5 runs/day × 5 min × 22 days = 550 min
- **Total: ~1,584 min/month**

**Result:** Under 2,000 limit with 400+ minutes buffer ✅

---

## Deployment Steps

### 1. Initialize Git Repository (if not already)

```bash
cd /Users/koppisettyeashameher/job-hunter

# Initialize repo
git init

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/job-hunter.git

# Create main branch
git checkout -b main
```

### 2. Add All Files

```bash
# Stage all files
git add .

# Commit
git commit -m "Phase 3: Add GitHub Actions workflows

- Greenhouse scraper (every 30 min)
- JobSpy scraper (every 2 hours)  
- Apify scraper (every 2 hours)
- Step 1 scoring (3x/day: noon, 3pm, 6pm)
- Step 2 tailoring (on-demand)
- Cover letter generator (conditional)
"

# Push to GitHub
git push -u origin main
```

### 3. Configure GitHub Secrets

Follow the guide in `GITHUB_SECRETS_SETUP.md` to add:

**Required (minimum):**
- SUPABASE_URL
- SUPABASE_KEY
- GROQ_API_KEY
- GEMINI_API_KEY
- NOTIFICATION_EMAIL

**Optional (for full features):**
- GMAIL_APP_PASSWORD
- APIFY_TOKEN
- GOOGLE_CREDENTIALS_JSON

### 4. Enable Actions

1. Go to your GitHub repo
2. Click "Actions" tab
3. If prompted, click "I understand my workflows, go ahead and enable them"
4. You should see all 5 workflows listed

### 5. Test a Workflow

1. Click on "Step 1 - Score Jobs & Send Digest"
2. Click "Run workflow" dropdown
3. Click "Run workflow" button
4. Wait 2-3 minutes
5. Check the run logs

If successful, all automatic runs will work!

---

## How to Use the Pipeline

### Daily Automated Flow (No Action Needed)

**Morning:**
- Pipeline scrapes jobs throughout the day
- Stores to database

**Noon, 3 PM, 6 PM:**
- Pipeline scores new jobs
- Emails you digest with top matches

**You receive:**
```
Subject: Job Digest — 12 high-scoring matches — Mar 26, 2026

7.8/10 | ML Engineer at Anthropic | Boston, MA
       Tech: Python, PyTorch, TensorFlow, GCP
       [View Job]

7.5/10 | Backend Engineer at Stripe | Remote
       Tech: Python, Go, PostgreSQL, AWS
       [View Job]
       
... (all jobs scoring 7.0+)
```

### When You Want to Apply:

**Option A: Via Command (Phase 3)**
```bash
# Get job IDs from digest email or database
gh workflow run step2_tailor.yml -f job_ids="job_id1,job_id2,job_id3"
```

**Option B: Via Web UI (Phase 4 - coming next)**
- Browse jobs in web interface
- Check boxes next to jobs
- Click "Process Selected"
- Wait 5 minutes
- Receive email with doc links

---

## Workflow Features

### Built-in Features:

✅ **Automatic retries** - If LLM fails, falls back to backup provider  
✅ **Error notifications** - Emails you if workflow fails  
✅ **Artifact uploads** - Saves logs for debugging  
✅ **Git commits** - Auto-commits generated markdown files  
✅ **Dependency caching** - Fast pip installs  
✅ **Manual triggers** - Can run any workflow on-demand  

### Security:

✅ **Secrets encrypted** - API keys never exposed in logs  
✅ **Supabase RLS** - Row-level security (optional)  
✅ **No hardcoded credentials** - Everything in secrets  

---

## Monitoring & Maintenance

### Check Workflow Status

1. Go to Actions tab
2. See all recent runs
3. Green checkmark = success
4. Red X = failure (you'll get email)

### View Logs

1. Click on any workflow run
2. Click on the job name
3. Expand each step to see logs

### Pause Workflows

To temporarily disable:
1. Go to Actions tab
2. Click on a workflow
3. Click "..." → "Disable workflow"

Re-enable the same way.

---

## What Happens Next (Phase 4)

With Phase 3 complete, the pipeline now runs automatically. Phase 4 adds the web UI so you can:

- Browse all scored jobs in a table
- Select jobs with checkboxes (no need for job IDs)
- Click "Process" to trigger Step 2
- Update job status (applied → interview → offer)
- View all past outputs
- See dashboard with stats

---

## Files Created

### Workflows:
- `.github/workflows/scrape_greenhouse.yml` (95 lines)
- `.github/workflows/scrape_jobspy.yml` (98 lines)
- `.github/workflows/scrape_apify.yml` (99 lines)
- `.github/workflows/step1_score.yml` (82 lines)
- `.github/workflows/step2_tailor.yml` (110 lines)

### Components:
- `src/cover_letter.py` (145 lines)

### Documentation:
- `GITHUB_SECRETS_SETUP.md` - Complete secrets guide
- `PHASE3_COMPLETE.md` - This file

### Updated:
- `src/main_tailor.py` - Added cover letter integration
- `src/output.py` - Added cover letter to markdown

---

## Testing Checklist

Before going live:

- [ ] Push code to GitHub
- [ ] Add all required secrets
- [ ] Manually trigger Step 1 workflow
- [ ] Verify it runs successfully
- [ ] Check you receive digest email (if GMAIL_APP_PASSWORD set)
- [ ] Manually trigger Step 2 with 1 job ID
- [ ] Verify outputs are created
- [ ] Check markdown file is committed

---

## Summary

**Phase 3 Status: COMPLETE ✅**

Pipeline is now fully automated:
- Scrapes jobs 18x/day (Greenhouse) + 5x/day (others)
- Scores jobs 3x/day
- Emails you digests 3x/day
- Tailors on-demand when you select jobs

**Ready to deploy to GitHub!**

Next: Phase 4 (Web UI) to make job selection easier than copy/pasting IDs.

**Estimated time to Phase 4:** 3-4 hours
**Current completion:** ~80%
