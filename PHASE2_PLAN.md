# Phase 2 Architecture Plan

## Overview

Phase 2 builds the complete automated job hunting pipeline on top of Phase 1's LLM foundation.

## Components to Build (from Section 18 of spec.md)

### Core Infrastructure

#### 1. Configuration (`src/config.py`)
- Centralized config for all API keys, URLs, settings
- Load from environment variables
- Greenhouse board URLs (top 40 companies)
- H1B filter keywords
- Rate limit thresholds

#### 2. Database Layer (`src/db.py`)
- Supabase client initialization
- CRUD operations for `jobs` table
- Dedup logic (30-day window)
- Status updates
- Query helpers (get scored jobs, get failed jobs, etc.)

#### 3. H1B Filter (`src/h1b_filter.py`)
- Keyword-based filtering (from Section 4)
- Returns: 'confirmed' | 'unknown' | 'blocked'
- Checks against 250 company list

### Scrapers

#### 4. Greenhouse Scraper (`src/scraper_greenhouse.py`)
- Custom JSON API scraper for 40 company boards
- Parse: title, location, description, URL
- Returns standardized job dict

#### 5. JobSpy Wrapper (`src/scraper_jobspy.py`)
- Wraps python-jobspy for Indeed/Google/Zip/LinkedIn
- Search queries from Section 4
- Fallback to Apify if LinkedIn rate limited

#### 6. Apify Scraper (`src/scraper_apify.py`)
- LinkedIn Jobs Scraper API
- Fallback only (when JobSpy LinkedIn fails)
- Uses `bebity/linkedin-jobs-scraper`

#### 7. Scraping Orchestrator (`src/main_scrape.py`)
- Calls appropriate scraper
- Deduplicates against Supabase
- Applies H1B filter
- Saves to database with status='seen'

### Scoring & Digest

#### 8. Job Scorer (`src/scorer.py`)
- LLM-based relevance scoring (1-10)
- Scoring criteria from Section 5
- Updates job records with scores

#### 9. Step 1 Main (`src/main_score.py`)
- Pulls unscored jobs from Supabase
- Runs scorer
- Generates digest email
- Sends via Gmail SMTP

### Tailoring & Output

#### 10. Step 2 Main (`src/main_tailor.py`)
- Pulls selected job IDs from workflow_dispatch input
- Runs resume tailor + email drafter
- Builds LaTeX PDF
- Creates Google Docs
- Updates Supabase with doc links
- Sends completion email

#### 11. Google Docs Creator (`src/google_docs.py`)
- Plain text Google Doc creation
- Resume doc + Email doc
- Set sharing permissions
- Return shareable links

#### 12. Email Notifier (`src/notifier.py`)
- Gmail SMTP client
- Digest email template
- Completion email template
- Error alert emails

#### 13. Rate Monitor (`src/rate_monitor.py`)
- Check Apify credit balance
- Check GitHub Actions minutes remaining
- Warning thresholds (20%)

#### 14. Markdown Output (`src/output.py`)
- Save to output/[date]/[company-role].md
- Include: resume + emails + metadata
- Permanent backup

### GitHub Actions Workflows

#### 15. Greenhouse Scraper (`.github/workflows/scrape_greenhouse.yml`)
- Runs every 30 min (weekdays, 9 AM - 6 PM EST)
- Calls `main_scrape.py --source greenhouse`

#### 16. JobSpy Scraper (`.github/workflows/scrape_jobspy.yml`)
- Runs every 2 hours (weekdays, 9 AM - 6 PM EST)
- Calls `main_scrape.py --source jobspy`

#### 17. Apify Scraper (`.github/workflows/scrape_apify.yml`)
- Runs every 2 hours (weekdays, 9 AM - 6 PM EST)
- Calls `main_scrape.py --source apify`

#### 18. Step 1 Processing (`.github/workflows/process_step1.yml`)
- Runs 3x/day (noon, 3 PM, 6 PM EST)
- Calls `main_score.py`
- Sends digest email

#### 19. Step 2 Processing (`.github/workflows/process_step2.yml`)
- On-demand (workflow_dispatch)
- Input: job IDs to process
- Calls `main_tailor.py`
- Creates PDFs and Google Docs

## Build Order for Phase 2

### Week 1: Core Infrastructure
1. `config.py` - Centralized configuration
2. `db.py` - Supabase integration + schema
3. `h1b_filter.py` - Keyword filtering
4. Test: Insert/query jobs from Supabase

### Week 2: Scrapers
5. `scraper_greenhouse.py` - 40 company boards
6. `scraper_jobspy.py` - JobSpy wrapper
7. `scraper_apify.py` - LinkedIn fallback
8. `main_scrape.py` - Orchestrator
9. Test: Scrape from each source, save to DB

### Week 3: Scoring & Digest
10. `scorer.py` - LLM relevance scoring
11. `notifier.py` - Gmail SMTP
12. `main_score.py` - Score + digest email
13. Test: Score jobs, receive digest email

### Week 4: Tailoring & Output
14. Complete `latex_builder.py` - Full parsing
15. `google_docs.py` - Doc creation
16. `output.py` - Markdown backup
17. `main_tailor.py` - Full Step 2 pipeline
18. Test: End-to-end tailoring with PDF + Docs

### Week 5: Automation
19. All 5 GitHub Actions workflows
20. Cron schedules (weekdays only)
21. workflow_dispatch for Step 2
22. Test: Let automation run for 1 day

## Dependencies to Add in Phase 2

```txt
# Already have: groq, google-generativeai, python-dotenv, pytest

# Add for Phase 2:
python-jobspy>=1.1.36      # Job scraping
supabase>=2.0.0            # Database
google-api-python-client   # Google Docs/Drive
google-auth                # Google auth
apify-client>=1.0.0        # LinkedIn fallback
```

## Testing Strategy

Each component gets:
1. Unit test (pytest)
2. Integration test with real APIs
3. Error handling test (rate limits, API failures)

## Estimated Effort

- **Phase 2 total:** 25-30 components
- **Phase 1 done:** 8 components ✓
- **Remaining:** ~20-22 components

## Next Immediate Steps

Once Groq rate limit resets:
1. Run full Phase 1 test (all 5 jobs, both providers)
2. Validate all outputs
3. Start Phase 2, beginning with `config.py` and `db.py`
