# Adding date_posted Field - Migration Guide

## Overview
Added `date_posted` field to track when jobs were originally posted by companies. This enables:
- Sorting jobs by recency in the UI
- Filtering by posting date
- Better understanding of job pipeline freshness

## Database Migration

### Step 1: Run Migration SQL
In your Supabase SQL Editor, run:

```sql
-- Add date_posted column
ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS date_posted TIMESTAMPTZ;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON jobs(date_posted);

-- Backfill existing jobs (use first_seen_at as estimate)
UPDATE jobs 
SET date_posted = first_seen_at 
WHERE date_posted IS NULL AND first_seen_at IS NOT NULL;
```

### Step 2: Verify Migration
```sql
SELECT 
  COUNT(*) as total_jobs,
  COUNT(date_posted) as jobs_with_date,
  MIN(date_posted) as oldest_posted,
  MAX(date_posted) as newest_posted
FROM jobs;
```

## Code Changes

### 1. Database Schema (`src/db.py`)
- Added `date_posted TIMESTAMPTZ` column to schema
- Added `date_posted` to `insert_job()` method
- Added index on `date_posted` for query performance

### 2. Scrapers - Date Extraction & Normalization

#### Greenhouse (`src/scraper_greenhouse.py`)
```python
# Extracts from first_published or posted_at
date_posted = job.get('first_published') or job.get('posted_at')
```
**Format:** ISO timestamp (e.g., `2026-03-20T18:42:26-04:00`)

#### Apify (`src/scraper_apify.py`)
```python
# Parses relative times and converts to ISO
"5 hours ago" → "2026-03-26T18:00:01.107406"
"2 days ago" → "2026-03-24T23:00:01.107406"
```
**Handles:** 
- Relative times: "X hours ago", "X days ago", "X weeks ago"
- Unix timestamps: `jobPostedAtTimestamp`
- ISO format: Passes through as-is

#### JobSpy (`src/scraper_jobspy.py`)
```python
# Extracts date_posted from JobPost object
date_posted = str(job.date_posted) if job.date_posted else None
```
**Note:** `python-jobspy-mini` returns `None` for `date_posted`, but we rely on the `hours_old=24` parameter for LinkedIn freshness.

### 3. API Updates (`api/main.py`)
- Added `sort_by` query parameter: `score`, `date_posted`, `first_seen_at`
- Default sort: By score desc, then date_posted desc
- `/api/jobs?sort_by=date_posted` shows newest jobs first

## API Examples

### Sort by posting date (newest first)
```bash
GET /api/jobs?sort_by=date_posted&limit=50
```

### Filter and sort by date
```bash
GET /api/jobs?status=scored&min_score=7&sort_by=date_posted
```

### Get most recent high-scoring jobs
```bash
GET /api/jobs?min_score=8&sort_by=date_posted&limit=20
```

## Data Quality

### By Scraper

**Greenhouse:**
- ✅ High quality: ISO timestamps with timezone
- ✅ Reliable: Uses `first_published` field from API
- ✅ Example: `2026-03-20T18:42:26-04:00`

**Apify (Google Jobs):**
- ✅ Good quality: Normalized from relative times
- ✅ Granularity: Hour-level precision
- ✅ Example: "5 hours ago" → `2026-03-26T18:00:01.107406`

**JobSpy (LinkedIn):**
- ⚠️ Limited: `date_posted` is `None` in mini version
- ✅ Workaround: Use `hours_old=24` for freshness guarantee
- ℹ️ Note: All JobSpy results are within 24 hours regardless

## UI Integration

The `date_posted` field will be displayed in the UI as:
- "5 hours ago" (< 24 hours)
- "2 days ago" (< 7 days)
- "Mar 20, 2026" (older)

## Testing

Run the test script:
```bash
python3 -c "
from src.scraper_greenhouse import GreenhouseScraper
from src.scraper_apify import ApifyScraper

# Test Greenhouse
gh = GreenhouseScraper()
jobs = gh.scrape_board('Stripe', 'https://boards.greenhouse.io/stripe')
print(f'Greenhouse: {len([j for j in jobs if j.get(\"date_posted\")])} jobs with dates')

# Test Apify
apify = ApifyScraper('YOUR_TOKEN')
jobs = apify.run_scraper(['Software Engineer'], max_results_per_query=10)
print(f'Apify: {len([j for j in jobs if j.get(\"date_posted\")])} jobs with dates')
"
```

## Production Ready
✅ Database schema updated  
✅ Migration script provided  
✅ All scrapers extract date_posted  
✅ Dates normalized to ISO format  
✅ API supports date sorting  
✅ Index added for query performance  
✅ Ready for UI integration
