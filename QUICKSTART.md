# Phase 1 Quick Start Guide

## You mentioned your API keys are already set as environment variables!

Since your `GROQ_API_KEY` and `GEMINI_API_KEY` are already set as environment variables, you can run the test immediately:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the test harness
python tests/test_harness.py
```

## What Will Happen

The test harness will process 5 jobs (each listed below) through BOTH Groq and Gemini:

### Test Job 1: Anthropic - Machine Learning Engineer (Boston, Hybrid)
- AI/ML role focused on foundation models, PyTorch, NLP
- Should trigger strong keyword matching
- Tests project swap logic (may keep existing ML projects)

### Test Job 2: Flatiron Health - Backend Engineer (Boston, On-site)
- Healthcare + backend + ETL pipelines + FHIR
- **Should swap in KidneyCare project** (healthcare CV, FHIR, FastAPI)
- Tests healthcare domain matching

### Test Job 3: Stripe - Software Engineer - Infrastructure (Remote US)
- Backend systems, distributed systems, APIs
- Tests backend skill reordering
- No project swap expected

### Test Job 4: Scale AI - AI Engineer (San Francisco)
- ML infrastructure, PyTorch, LLM evaluation
- Tests ML infrastructure matching
- Should emphasize OK AI experience

### Test Job 5: Wayfair - Full Stack Engineer (Boston, Hybrid)
- Full stack + data pipelines + React + Python
- Tests full stack skill balancing
- Boston location should be highlighted

## Expected Output Structure

```
test_output/
├── SUMMARY.md                                    # Side-by-side comparison report
├── Anthropic_Machine_Learning_Engineer_groq.json      # Full Groq result data
├── Anthropic_Machine_Learning_Engineer_groq_resume.txt
├── Anthropic_Machine_Learning_Engineer_groq_emails.txt
├── Anthropic_Machine_Learning_Engineer_gemini.json
├── Anthropic_Machine_Learning_Engineer_gemini_resume.txt
├── Anthropic_Machine_Learning_Engineer_gemini_emails.txt
└── ... (same pattern for all 5 jobs)
```

## What to Look For

### Resume Quality Checks
- ✅ All 4 work experiences included (OK AI, TA, Info Edge, Pharmeasy)
- ✅ Under 3,500 characters (approximately 1 page)
- ✅ Natural, conversational tone (not templated)
- ✅ Skills reordered to match JD keywords
- ✅ No banned phrases (leveraged, spearheaded, utilized, orchestrated)
- ✅ Only approved metrics used (no invented numbers)
- ✅ Project swap for healthcare jobs (KidneyCare for Flatiron Health)

### Cold Email Quality Checks
- ✅ Two versions per job (hiring manager + recruiter)
- ✅ 5 sentences max
- ✅ Subject line: "Interested in [Role] — [differentiator]"
- ✅ Sounds human, not template-like
- ✅ No fluff or banned phrases
- ✅ Clear low-pressure ask

### Guardrail Results
Each job will show:
1. **Hallucination:** Pass/fail with flagged items
2. **Banned Phrases:** Pass/fail with found phrases
3. **Keyword Match:** Score (%) - informational only
4. **Length:** Pass/fail with character count

## Groq vs Gemini Comparison

The SUMMARY.md will show:
- Which provider has higher keyword match scores
- Which provider stays within length limits better
- Which provider produces more natural-sounding text
- Overall pass rates for each guardrail

## If You Need to Iterate

After reviewing output, you can:

1. **Adjust prompts** in `src/resume_tailor.py` or `src/email_drafter.py`
2. **Tune guardrails** in `src/guardrails.py`
3. **Re-run tests:** `python tests/test_harness.py`
4. **Compare new vs old output**

## Estimated Runtime

- **With API keys:** ~2-3 minutes total
  - ~10-15 seconds per job per provider
  - Groq is faster, Gemini is slightly slower
- **5 jobs × 2 providers = 10 LLM calls**

## Sample Output Preview

Each resume will look like:

```
Easha Meher Koppisetty
mehereasha2601@gmail.com 8572943442 Boston, MA https://www.linkedin.com/in/easha-meher
https://github.com/mehereasha2601 https://mehereasha2601.github.io/

EDUCATION

Northeastern University
Master of Science in Artificial Intelligence
Jan 2024 – May 2026 | Boston, MA
Relevant Coursework: [reordered to match JD keywords]

[... continues with all sections ...]
```

Each email will look like:

```
=== HIRING MANAGER VERSION ===
Subject: Interested in Backend Engineer — built healthcare CV at 96% accuracy

[5 sentences max, personal tone, mentions specific product/mission]

=== RECRUITER VERSION ===
Subject: Interested in Backend Engineer — MS in AI, healthcare ML experience

[5 sentences max, professional tone, emphasizes qualifications]
```

## Ready to Run

Since your environment variables are already set:

```bash
source venv/bin/activate
python tests/test_harness.py
```

Then review `test_output/SUMMARY.md` and individual output files.
