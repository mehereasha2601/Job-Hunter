# Job Hunter Pipeline

Automated job hunting pipeline that scrapes job listings, scores relevance, tailors resumes, and generates cold emails using LLMs.

**Version:** 2.0 (March 26, 2026)

## Current Status: Phase 2 Complete ✅

### Phase 1: LLM Components (Complete)
- LLM client (Groq + Gemini fallback)
- Resume tailor with strict 1-page enforcement
- Cold email drafter (2 versions)
- 4 guardrails (hallucination, banned phrases, keywords, length)
- Test harness with 5 sample jobs

### Phase 2: Core Pipeline (Complete)
- 3 job scrapers (Greenhouse, JobSpy, Apify)
- H1B filtering
- Supabase database integration
- LLM-powered relevance scoring
- Step 1: Scrape → Score → Digest email
- Step 2: Tailor → Generate docs → Completion email
- Rate limit monitoring

### Phase 3: Automation (Next)
- GitHub Actions workflows
- Cron scheduling
- Web UI for job selection
- OAuth flows

---

## Quick Start

### Phase 1 Testing (works now)

1. **Install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Set up API keys:**
```bash
cp .env.example .env
# Edit .env and add:
# - GROQ_API_KEY
# - GEMINI_API_KEY
```

3. **Run test harness:**
```bash
source venv/bin/activate
python tests/test_harness.py
```

4. **Review results:**
- Check `test_output/SUMMARY.md` for comparison
- Review individual outputs in `test_output/`

### Phase 2 Setup (requires Supabase)

1. **Set up Supabase:**
   - Follow detailed instructions in `SUPABASE_SETUP.md`
   - Create project, run schema, get credentials

2. **Configure environment:**
```bash
# Add to .env:
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
NOTIFICATION_EMAIL=your_email@gmail.com
```

3. **Run the pipeline:**

**Daily Scraping:**
```bash
python src/main_scrape.py
```

**Daily Scoring:**
```bash
python src/main_score.py
```

**Tailoring (for selected jobs):**
```bash
python src/main_tailor.py <job_id1> <job_id2> <job_id3>
```

---

## Project Structure

```
job-hunter/
├── src/
│   ├── config.py                    # Central configuration
│   ├── db.py                        # Supabase client + schema
│   ├── llm.py                       # LLM client (Groq + Gemini)
│   ├── h1b_filter.py                # H1B sponsor filtering
│   ├── scraper_greenhouse.py        # Greenhouse scraper (40 boards)
│   ├── scraper_jobspy.py            # LinkedIn/Indeed/ZipRecruiter
│   ├── scraper_apify.py             # Google Jobs scraper
│   ├── main_scrape.py               # Scraping orchestrator
│   ├── scorer.py                    # LLM relevance scorer
│   ├── main_score.py                # Step 1: Score + digest
│   ├── resume_tailor.py             # Resume generation
│   ├── email_drafter.py             # Cold email generation
│   ├── guardrails.py                # Quality validation
│   ├── main_tailor.py               # Step 2: Tailor + output
│   ├── google_docs.py               # Google Docs creation
│   ├── output.py                    # Markdown backups
│   ├── notifier.py                  # Email notifications
│   ├── rate_monitor.py              # API limit tracking
│   └── latex_builder.py             # PDF generation
├── tests/
│   ├── test_harness.py              # Phase 1 test runner
│   ├── test_jobs.json               # Sample job listings
│   └── test_gemini_only.py          # Gemini-only test
├── templates/
│   └── resume.tex                   # LaTeX resume template
├── output/                          # Markdown backups (date-based)
├── test_output/                     # Phase 1 test results
├── requirements.txt                 # All dependencies
├── resume.txt                       # Master resume
├── spec.md                          # Complete specification
└── h1b-companies.md                 # 250 target companies
```

---

## Pipeline Flow

### Step 1: Scraping + Scoring (Automated Daily)

```
Scrape Jobs
  ├── Greenhouse (40 company boards)
  ├── JobSpy (LinkedIn, Indeed, ZipRecruiter)
  └── Apify (Google Jobs)
        ↓
H1B Filter (skip blocked companies)
        ↓
Supabase (store with status='seen')
        ↓
LLM Scorer (score 1-10 based on 4 criteria)
        ↓
Supabase (update with scores, status='scored')
        ↓
Digest Email (jobs scoring 7.0+ sent to your inbox)
```

### Step 2: Tailoring (Manual Selection)

```
Select Jobs (from digest or web UI)
        ↓
Tailor Resume (1-page, job-specific)
        ↓
Draft Cold Emails (hiring manager + recruiter versions)
        ↓
Run Guardrails (4 checks for quality)
        ↓
Create Outputs
  ├── Google Docs (resume + emails)
  ├── Markdown backup (version control)
  └── PDF (from LaTeX template)
        ↓
Update Supabase (status='tailored', save links)
        ↓
Completion Email (with all doc links)
```

---

## Key Features

### Intelligent Filtering
- ✅ H1B sponsor validation (250 target companies)
- ✅ Blocking keyword detection (citizenship, clearance, etc.)
- ✅ Automatic deduplication (30-day window)

### LLM-Powered Scoring
- ✅ 4 criteria: H1B friendliness, tech stack, location, company tier
- ✅ Location bonus (Boston +2, Remote +1)
- ✅ Tech stack extraction

### Quality Guardrails
- ✅ Hallucination detection (no invented facts)
- ✅ Banned phrase filter (leveraged, spearheaded, etc.)
- ✅ Keyword match scoring (JD alignment)
- ✅ Length validation (strict 1-page limit)

### Resume Tailoring
- ✅ Reorders coursework and skills to match JD
- ✅ Rephrases bullets with STAR format + metrics
- ✅ Preserves all 4 work experiences
- ✅ Smart project swapping (KidneyCare for healthcare roles)
- ✅ Strictly 1 page (3,500 char limit)

### Output Generation
- ✅ Google Docs (shareable links)
- ✅ PDF from LaTeX
- ✅ Markdown backups (git version control)
- ✅ Email notifications

---

## API Keys & Services

### Required for Phase 1:
- **Groq** (free): https://console.groq.com
- **Gemini** (free): https://aistudio.google.com

### Required for Phase 2:
- **Supabase** (free): https://supabase.com
  - See `SUPABASE_SETUP.md` for setup guide

### Optional for Phase 2:
- **Apify** (free tier): https://apify.com
  - For Google Jobs scraping
- **Gmail App Password**: https://myaccount.google.com/apppasswords
  - For email notifications
- **Google Service Account**: https://console.cloud.google.com
  - For creating Google Docs

---

## Critical Rules from Spec

### Resume:
- Strictly 1 page max (3,500 chars)
- All 4 work experiences ALWAYS included
- Only approved metrics (12x, 30%, 200K+, etc.)
- STAR format with quantifiable results
- No invented facts

### Cold Emails:
- 5 sentences max
- Two versions (hiring manager + recruiter)
- Subject format: "Interested in [Role] — [differentiator]"
- Human, conversational tone
- No banned phrases

### Banned Phrases:
- leveraged, spearheaded, utilized, orchestrated
- passionate about, thrilled to apply, excited to bring
- I hope this email finds you well
- I believe I would be a great fit

---

## Documentation

- `spec.md` - Complete project specification (the bible)
- `PHASE1_COMPLETE.md` - Phase 1 results and validation
- `PHASE2_COMPLETE.md` - Phase 2 architecture summary
- `SUPABASE_SETUP.md` - Step-by-step database setup
- `h1b-companies.md` - 250 target companies with H1B history

---

## Testing

### Phase 1 Test Harness:
```bash
source venv/bin/activate
python tests/test_harness.py
```

Tests 5 diverse job descriptions with both Groq and Gemini, validates guardrails, generates comparison report.

### Phase 2 Component Tests:
```bash
# Test database connection
python -c "from src.db import Database; db = Database(); print('DB OK')"

# Test H1B filter
python -c "from src.h1b_filter import h1b_filter; print(h1b_filter.check_company('Anthropic'))"

# Test config validation
python -c "from src.config import Config; print(Config.validate())"
```

---

## Development

Built following strict specification in `spec.md`:
- All metrics verified and approved
- STAR format preserved
- All work experiences included
- 1-page limit enforced
- Banned phrases filtered
- H1B sponsor validation

**Quality:** Validated in Phase 1 with 9/10 output quality score.

---

## License

Personal project for Easha Meher's job search.
