# What's Left To Do - Phase 3 & Beyond

**Current Status:** Phase 1 ✅ + Phase 2 ✅ = ~70% Complete

---

## Phase 3: GitHub Actions & Automation (NEXT)

### What Needs to Be Built

#### 1. GitHub Actions Workflows (5 workflows)
- [ ] `.github/workflows/scrape_greenhouse.yml` - Daily Greenhouse scraping
- [ ] `.github/workflows/scrape_jobspy.yml` - Daily JobSpy (LinkedIn/Indeed/Zip)
- [ ] `.github/workflows/scrape_apify.yml` - Daily Apify (Google Jobs)
- [ ] `.github/workflows/step1_score.yml` - Daily scoring + digest email
- [ ] `.github/workflows/step2_tailor.yml` - Manual trigger for tailoring

#### 2. Workflow Features
- [ ] Cron scheduling (daily at 8am ET)
- [ ] workflow_dispatch triggers (manual runs)
- [ ] Secrets configuration (API keys)
- [ ] Error notifications
- [ ] Run summaries

#### 3. Additional Scripts
- [ ] Cover letter generator (conditional, if JD requires it)
- [ ] LaTeX → PDF compilation in Actions
- [ ] Google Drive upload for PDFs

**Estimated effort:** 2-3 hours

---

## Phase 4: Web UI (AFTER Phase 3)

### What Needs to Be Built

#### 1. Frontend (index.html + app.js)
- [ ] Job browser table (sortable, filterable)
- [ ] Checkboxes for job selection
- [ ] "Process Selected" button → triggers workflow_dispatch
- [ ] Status dropdown per job (seen → applied → interview → offer)
- [ ] View past outputs (links to Google Docs + markdown)
- [ ] Dashboard with stats (total scraped, tailored, applied, by company)

#### 2. Authentication
- [ ] Client-side password gate (JS)
- [ ] Password stored in config

#### 3. Supabase Integration
- [ ] Supabase JS client (`supabase-js`)
- [ ] Real-time data fetching
- [ ] Status updates via UI

#### 4. Styling
- [ ] Modern, clean UI (Tailwind CSS or similar)
- [ ] Mobile-responsive
- [ ] Dark mode toggle

#### 5. Hosting
- [ ] GitHub Pages setup
- [ ] Deploy script

**Estimated effort:** 3-4 hours

---

## Phase 5: Polish & Go Live (FINAL)

### What Needs to Be Done

#### 1. End-to-End Testing
- [ ] Run full pipeline with real data (10-20 jobs)
- [ ] Verify all outputs (resumes, emails, docs, PDFs)
- [ ] Check guardrails on real output
- [ ] Test web UI → workflow trigger

#### 2. Documentation
- [ ] User guide for daily workflow
- [ ] Troubleshooting guide
- [ ] API setup instructions

#### 3. Monitoring
- [ ] Set up rate limit warnings
- [ ] Error alerting
- [ ] Usage tracking

#### 4. Iteration
- [ ] Monitor first week of outputs
- [ ] Adjust prompts based on real results
- [ ] Fine-tune scoring criteria

**Estimated effort:** 1-2 hours setup + ongoing monitoring

---

## Current Progress Checklist

### ✅ Phase 1: LLM Components (COMPLETE)
- ✅ LLM client (Groq + Gemini)
- ✅ Resume tailor
- ✅ Email drafter
- ✅ Guardrails (all 4)
- ✅ Test harness
- ✅ LaTeX template + builder

### ✅ Phase 2: Core Pipeline (COMPLETE)
- ✅ Config system
- ✅ Database (Supabase)
- ✅ H1B filter (250 companies)
- ✅ Greenhouse scraper
- ✅ JobSpy wrapper
- ✅ Apify wrapper
- ✅ Scraping orchestrator
- ✅ LLM scorer
- ✅ Step 1 (score + digest)
- ✅ Step 2 (tailor + output)
- ✅ Email notifier
- ✅ Google Docs client
- ✅ Markdown backup
- ✅ Rate monitor
- ✅ Rate limiting strategy

### ⏳ Phase 3: Automation (NEXT - ~2-3 hours)
- [ ] 5 GitHub Actions workflows
- [ ] Cron scheduling
- [ ] Manual triggers
- [ ] Secrets setup
- [ ] Cover letter generator

### ⏳ Phase 4: Web UI (~3-4 hours)
- [ ] Job browser interface
- [ ] Selection checkboxes
- [ ] Status tracking
- [ ] Dashboard
- [ ] Password protection
- [ ] GitHub Pages hosting

### ⏳ Phase 5: Launch (~1-2 hours)
- [ ] End-to-end testing
- [ ] Documentation
- [ ] Monitoring setup
- [ ] Go live

---

## Time Estimate to Complete

| Phase | Effort | Status |
|-------|--------|--------|
| Phase 1 | ✅ Done | 100% |
| Phase 2 | ✅ Done | 100% |
| Phase 3 | 2-3 hours | 0% |
| Phase 4 | 3-4 hours | 0% |
| Phase 5 | 1-2 hours | 0% |

**Total remaining:** 6-9 hours of build time

**Current completion:** ~70%

---

## What Can You Do NOW (Before Phase 3)

### 1. Test the Pipeline Manually

**When rate limits reset:**
```bash
# Step 1: Score jobs
python -m src.main_score

# Step 2: Tailor a job
python -m src.main_tailor <job_id>
```

### 2. Set Up Optional Services

- [ ] Gmail App Password (for email notifications)
- [ ] Apify account (for Google Jobs scraping)
- [ ] Google Service Account (for Docs creation)

### 3. Add More Test Jobs

You can add real job descriptions to test with:
```bash
python -c "
from src.db import Database

db = Database()
db.insert_job({
    'title': 'Your Real Job Title',
    'company': 'Company Name',
    'url': 'https://...',
    'description': '...',
    # ...
})
"
```

---

## Immediate Next Step: Phase 3

Build the GitHub Actions workflows to automate:
1. Daily scraping (8am ET)
2. Daily scoring + digest email (9am ET)
3. Manual tailoring trigger (via web UI or command)

This will make the pipeline fully autonomous - you just check your email digest each morning and select jobs to tailor.

**Ready to start Phase 3?**
