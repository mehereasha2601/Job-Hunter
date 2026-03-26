# Rate Limiting Strategy for Production

**Analysis Date:** March 26, 2026

---

## Current Rate Limits

### Groq (Free Tier)
- **30 requests per minute (RPM)**
- **14,400 requests per day (RPD)**
- **100,000 tokens per day (TPD)** ← Bottleneck

### Gemini (Free Tier)
- **1,500 requests per day (RPD)**
- **1,000,000 tokens per day (TPD)**

---

## Production Usage Estimate

### Daily Pipeline Run

**Scraping (0 LLM calls):**
- Greenhouse: 40 boards
- JobSpy: 18 queries (6 titles × 3 locations)
- Apify: 18 queries
- **LLM calls:** 0

**Scoring (1 LLM call per job):**
- Typical daily scrape: 50-200 new jobs
- Each score call: ~1,500 tokens (resume + JD + reasoning)
- **Estimate:** 100 jobs/day × 1,500 tokens = 150,000 tokens

**Tailoring (3 LLM calls per job):**
- Resume: ~2,000 tokens
- Email (hiring manager): ~1,000 tokens
- Email (recruiter): ~1,000 tokens
- Total per job: ~4,000 tokens
- Typical: 5-10 jobs tailored per day
- **Estimate:** 10 jobs × 4,000 = 40,000 tokens

**Total Daily Usage:**
- Scoring: 150,000 tokens
- Tailoring: 40,000 tokens
- **Total: 190,000 tokens/day**

---

## Problem: We Will Exceed Groq's 100K Token Limit

### Reality Check

With 100 jobs/day to score:
- Groq: 100K tokens = ~66 jobs max
- We need ~190K tokens/day for typical usage

**Groq free tier is insufficient for production.**

---

## Solution Options

### Option A: Use Gemini as Primary (FREE, Recommended for MVP)

Gemini's 1,500 RPD and 1M tokens/day are more than enough.

**Changes needed:**
1. Switch `src/llm.py` to prefer Gemini first (1 line change)
2. Keep Groq as fallback
3. Add exponential backoff for rate limit retries

**Pros:**
- ✅ Fits within free tier easily
- ✅ No billing needed
- ✅ 1-line code change
- ✅ Works TODAY

**Cons:**
- ⚠️ Gemini quality is slightly lower than Groq (Phase 1: 8/10 vs 9/10)
- ⚠️ May need prompt adjustments

**Monthly cost:** $0

---

### Option B: Upgrade Groq to Pay-As-You-Go (Recommended for Production)

Groq Pay-As-You-Go tier:
- **$0.59 per 1M input tokens**
- **$0.79 per 1M output tokens**
- **No daily limits**
- **Same speed and quality**

**Cost estimate:**
- 190K tokens/day = 0.19M tokens/day
- Input: ~120K tokens = $0.07/day
- Output: ~70K tokens = $0.06/day
- **Total: ~$0.13/day = $4/month**

**Pros:**
- ✅ Better quality than Gemini
- ✅ Extremely cheap ($4/month)
- ✅ No request limits
- ✅ No code changes needed

**Cons:**
- 💳 Requires credit card
- 💳 Need to monitor spend (but it's tiny)

**Monthly cost:** ~$4

---

### Option C: Hybrid Approach (Best of Both Worlds)

Use Gemini for scoring, Groq for tailoring:

**Scoring (100 jobs/day):**
- Use Gemini (150K tokens/day)
- Scoring quality matters less (just need 1-10)
- Fits in Gemini's 1M token limit easily

**Tailoring (10 jobs/day):**
- Use Groq (40K tokens/day)
- Fits in Groq's 100K token limit
- Higher quality matters for final output

**Pros:**
- ✅ Stays within both free tiers
- ✅ Uses best model for each task
- ✅ No billing needed
- ✅ Best quality/cost ratio

**Cons:**
- ⚠️ More complex logic
- ⚠️ Need to handle both rate limits

**Monthly cost:** $0

---

## Token Usage Breakdown by Task

| Task | Tokens | Why |
|------|--------|-----|
| Score 1 job | 1,500 | Resume (800) + JD (500) + System prompt (100) + Response (100) |
| Tailor resume | 2,000 | Resume (800) + JD (500) + System prompt (400) + Output (300) |
| Draft 1 email | 1,000 | Resume (800) + JD (500) + System prompt (300) + Output (100) |

### Per-Job Total:
- Scoring: 1,500 tokens
- Tailoring: 4,000 tokens (resume + 2 emails)
- **Full pipeline per job: 5,500 tokens**

### Daily Capacity:

**Groq (100K):**
- Scoring only: 66 jobs
- Full pipeline: 18 jobs
- **Insufficient**

**Gemini (1M):**
- Scoring only: 666 jobs
- Full pipeline: 181 jobs
- **More than enough**

**Groq Paid (unlimited):**
- Scoring: unlimited at $0.001/job
- Full pipeline: unlimited at $0.003/job
- **$0.30 for 100 jobs**

---

## Recommended Implementation: Option C (Hybrid)

### Code Changes Needed

**1. Update `src/llm.py` to accept provider preference:**

```python
def call(
    self,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    prefer_provider: str = 'groq'  # <-- NEW parameter
) -> Dict[str, Any]:
    """Call LLM with provider preference."""
    
    # Order providers based on preference
    if prefer_provider == 'gemini':
        providers = ['gemini', 'groq']
    else:
        providers = ['groq', 'gemini']
    
    # Try each provider in order
    for provider in providers:
        # ... existing code ...
```

**2. Update `src/scorer.py` to use Gemini:**

```python
def score_job(self, job: Dict) -> Tuple[float, str]:
    # ... existing code ...
    
    llm_result = self.llm.call(
        system_prompt,
        user_prompt,
        prefer_provider='gemini'  # <-- Use Gemini for scoring
    )
```

**3. Keep `src/resume_tailor.py` using Groq (default):**

```python
def tailor_resume(self, ...):
    # ... existing code ...
    
    llm_result = self.llm.call(
        system_prompt,
        user_prompt,
        prefer_provider='groq'  # <-- Use Groq for quality
    )
```

**4. Keep `src/email_drafter.py` using Groq (default):**

```python
def draft_emails(self, ...):
    # Already defaults to Groq
```

---

## Daily Token Budget with Hybrid

| Task | Provider | Tokens/Day | Limit | Headroom |
|------|----------|------------|-------|----------|
| Score 100 jobs | Gemini | 150K | 1M | 850K (85%) |
| Tailor 10 jobs | Groq | 40K | 100K | 60K (60%) |

**Result:** Both fit comfortably within free tiers!

---

## Fallback Strategy

With hybrid approach, if one provider hits limit:

**If Gemini hits limit during scoring:**
- ✅ Falls back to Groq
- ⚠️ Groq will hit limit after ~66 jobs
- 📧 Rate monitor sends warning email
- 🛑 Scoring stops, resume next day

**If Groq hits limit during tailoring:**
- ✅ Falls back to Gemini
- ✅ Gemini has plenty of capacity
- ⚠️ Slightly lower quality output

**Safety net:** Two independent free tiers = very robust

---

## Long-Term Scaling

### If you get 200+ jobs/day:

**Month 1-2 (while actively searching):**
- Upgrade Groq to paid: $4/month
- Keep Gemini as free fallback
- Total cost: $4/month for unlimited

**Month 3+ (maintenance mode):**
- Job search complete
- Turn off pipeline or reduce frequency
- Cost: $0

---

## My Strong Recommendation

**Implement Option C (Hybrid) NOW:**

1. It's free forever
2. It works within rate limits
3. It uses the best model for each task
4. It's production-ready

**The code changes are minimal** (~10 lines total).

Should I implement the hybrid approach now? It will take 5 minutes and make your pipeline production-ready at $0/month cost.

Or would you prefer:
- Option A: Just flip to Gemini-first (1 line)
- Option B: Keep current, plan to upgrade Groq to paid later
