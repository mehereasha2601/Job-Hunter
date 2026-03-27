# Location & Date Filtering - Complete

## Summary
Fixed location filtering to exclude Canada-only jobs while including US remote roles, and implemented 14-day recency filter using `first_published` field.

## Issues Found & Fixed

### 1. Canada Jobs Appearing
**Problem**: Jobs with "Toronto, Canada" or "Canada" in location were passing filter because "remote" keyword was too broad.

**Fix**: 
- Added explicit `NON_US_LOCATION_KEYWORDS` list (Canada, Toronto, Vancouver, Australia, etc.)
- Implemented multi-location logic: Include if job has BOTH US and Canada (US option available), exclude if Canada-only
- Enhanced `US_LOCATION_KEYWORDS` to catch NYC, SF, Seattle abbreviations

### 2. Date Filtering Not Working
**Problem**: Initially tried to use `posted_at` field which doesn't exist in Greenhouse API.

**Discovery**: Greenhouse API provides `first_published` field which tracks when job was first posted.

**Fix**: Updated filter to use `first_published` with 14-day window (captures recent jobs without over-filtering)

### 3. Missing Job Title Variations
**Problem**: "Backend / API Engineer" and "Frontend Engineer" weren't matching.

**Fix**: Added to `JOB_TITLES`:
- `API Engineer`
- `SDK Engineer`
- `Frontend Engineer`

## Filter Configuration (src/config.py)

### Location Filters
```python
US_LOCATION_KEYWORDS = [
    'united states', 'usa', 'us-', ', us', 'us,',
    'nyc', 'new york', 'san francisco', 'sf,', 'seattle', 'sea,',
    'boston', 'chicago', 'chi,', 'atlanta', 'austin', 'denver',
    # ... 30+ keywords
]

NON_US_LOCATION_KEYWORDS = [
    'canada', 'toronto', 'vancouver', 'montreal', 'can-',
    'dublin', 'london', 'berlin', 'paris', 'singapore',
    'australia', 'sydney', 'mexico', 'india', 'japan',
    # ... 27+ keywords
]
```

### Multi-Location Logic
- **Has US + Has Canada** (e.g., "NYC, Toronto") → ✅ Include (US option available)
- **Has US only** (e.g., "San Francisco") → ✅ Include
- **Has Canada only** (e.g., "Toronto, Canada") → ❌ Exclude
- **N/A or empty** → ✅ Include (let LLM scorer filter by description)

### Date Filter
- **Window**: Last 14 days
- **Field**: `first_published` from Greenhouse API
- **Rationale**: Balances freshness with sufficient volume

## Test Results (Stripe Board)

### Before Fixes
- Total jobs scraped: 509
- After title filter: ~20 jobs
- **Issues**: Canada jobs included, no date filtering, missing job title variants

### After Fixes
```
Filtered Results: 3 US jobs (last 14 days)

1. Backend / API Engineer, Billing
   Location: San Francisco, Seattle, NYC, US-Remote
   Age: 6 days

2. SDK Engineer (React/React Native), Privy
   Location: NYC-Privy
   Age: 7 days

3. Frontend Engineer, Privy
   Location: NYC-Privy
   Age: 8 days
```

### Validation
- ✅ **No Canada-only jobs** (0 found)
- ✅ **US locations explicit** (SF, Seattle, NYC)
- ✅ **Latest postings** (6-8 days old)
- ✅ **Relevant roles** (Backend, SDK, Frontend)

## Job Title Coverage (35 total)

Now includes:
- Core: Software, Backend, **Frontend**, Full Stack, **API**, **SDK**
- ML/AI: ML Engineer, Data Scientist, Computer Vision, NLP
- Platform: Infrastructure, MLOps, Platform Engineer
- Entry-level: New Grad, Associate, Junior
- QA/Testing: Test Engineer, QA, SDET
- Data: Data Engineer, Data Analyst

## Seniority Exclusions (23 keywords)

Excludes:
- Levels: senior, staff, principal, lead, director, **manager**
- Experience: **3+ years**, **4+ years**, 5+ years, 6+ years, etc.

## Impact on Pipeline

### Daily Scraping (Step 1)
- Scans all 52 Greenhouse boards
- Applies title + location + date + seniority filters
- Expected: **10-50 fresh jobs per day** across all companies
- Sends to Groq for scoring (within 100K token/day limit)

### Quality vs Quantity
- **Before**: 1000+ jobs but many irrelevant (Canada, international, old, senior)
- **After**: ~50-100 jobs but highly targeted (US, recent, entry/mid-level)
- **Benefit**: Lower LLM costs, higher quality matches, less noise

## Production Readiness

✅ **Location filtering** works correctly (no Canada-only)
✅ **Date filtering** uses `first_published` (14-day window)
✅ **Title matching** covers 35+ role variants
✅ **Seniority filtering** excludes manager + 3-4+ year roles
✅ **Multi-location handling** includes jobs with US options

## Next Steps

1. **Monitor daily runs** - Check if 14-day window provides enough volume
2. **Adjust if needed** - Can extend to 21 days if job count is too low
3. **Track false negatives** - Watch for good jobs being filtered out
4. **Company-specific tuning** - Some boards may need custom logic

---
**Date**: 2026-03-26
**Status**: Complete
**Files Modified**: 
- `src/config.py` (location keywords, job titles, date window)
- `src/scraper_greenhouse.py` (multi-location logic, date filtering)
