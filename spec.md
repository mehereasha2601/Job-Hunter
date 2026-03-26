# Job Hunter Pipeline — Complete Specification

**Version:** 1.0 (Finalized March 26, 2026)
**Owner:** Easha Meher Koppisetty

---

## 1. Architecture Overview

### Two-step pipeline

**Step 1 — Scrape & Score (automated):**
Scrape → dedup → H1B hard filter → LLM relevance scoring → digest email with scored list

**Step 2 — Tailor & Output (manually triggered via web UI):**
User selects jobs in UI → tailor resume → generate cold emails → (optional) cover letter → create Google Docs → email notification + UI update

### Tech stack
- **Language:** Python 3.11+
- **Scraping:** JobSpy (Indeed, Google Jobs, ZipRecruiter), Apify fallback (LinkedIn only), Custom (Greenhouse JSON API)
- **LLMs:** Groq (primary, Llama 3.3 70B) + Google Gemini Flash (fallback)
- **Storage:** Supabase (free tier PostgreSQL)
- **Output:** LaTeX → PDF (resume), Google Docs (shareable backup), Gmail SMTP (app password)
- **Scheduler:** GitHub Actions (cron)
- **Web UI:** GitHub Pages (static HTML, password protected)
- **Resume source:** Google Doc (pipeline pulls latest)

---

## 2. Schedule

**All times EST. Weekdays only (Mon–Fri).**

| Job | Frequency | Time window | Est. minutes/run |
|-----|-----------|-------------|------------------|
| Greenhouse scrape | Every 30 min | 9 AM – 6 PM | ~1 min |
| JobSpy scrape (Indeed/Google/Zip) | Every 2 hours | 9 AM – 6 PM | ~2 min |
| Apify scrape (LinkedIn fallback) | Every 2 hours | 9 AM – 6 PM | ~2 min |
| Step 1 processing (score + digest email) | 3x/day | Noon, 3 PM, 6 PM | ~3 min |
| Step 2 processing (tailor + output) | On-demand via UI | Within 30 min of trigger | ~5 min |

**Monthly budget:**
- Greenhouse scrapes: 18 runs/day × 1 min × 22 days = ~396 min
- JobSpy + Apify scrapes: 5 runs/day × 2 min × 22 days × 2 = ~440 min
- Step 1 processing: 3 runs/day × 3 min × 22 days = ~198 min
- Step 2 processing: ~5 runs/day × 5 min × 22 days = ~550 min (estimate)
- **Total: ~1,584 min/month** (under 2,000 free limit)

---

## 3. Job Sources

### Greenhouse boards (free, every 30 min) — Top 40
**National:**
Anthropic, Scale AI, Databricks, Perplexity, Stripe, Cloudflare, Datadog, Ramp, Flatiron Health, MongoDB, Snowflake, Confluent, Twilio, Airbnb, DoorDash, Pinterest, Figma, Notion, Duolingo, Grammarly, HubSpot, GitLab, Fivetran, dbt Labs, Pinecone, Together AI, Robinhood, Plaid, Wiz, Grafana Labs

**Boston-focused:**
Klaviyo, Wayfair, Toast, Chewy, CarGurus, DataRobot, Athenahealth, Foundation Medicine, Whoop, Benchling

### JobSpy scrapers (free, no API key — every 2 hours)
- Indeed (most reliable, no rate limiting)
- Google Jobs
- ZipRecruiter
- LinkedIn (attempted first; if rate-limited, falls back to Apify)
- Glassdoor skipped (unreliable, frequent 403 errors)

### Apify scrapers (LinkedIn only, fallback — every 2 hours)
- LinkedIn Jobs Scraper (`bebity/linkedin-jobs-scraper`)
- Only used because LinkedIn aggressively blocks non-Apify scraping

### Full company target list
250 companies across 14 tiers (see h1b-companies.md)

---

## 4. Search Queries & Filters

### Job titles
- Software Engineer
- ML Engineer / AI Engineer
- Backend Engineer
- Full Stack Engineer

### Seniority
- Entry level / New Grad
- Mid level (2-4 years)
- Exclude: Senior (5+ years)

### Location priority
- Anywhere in US, but **Boston gets a scoring bonus**
- Priority order: Boston on-site/hybrid > Remote US > Other US cities

### H1B hard filter
**Automatically skip** any job containing:
- "US citizen" / "US citizenship required"
- "no sponsorship" / "will not sponsor"
- "security clearance" / "clearance required"
- "must be a US person" / "ITAR"

---

## 5. Job Relevance Scoring

LLM scores each job 1-10 based on these criteria (in priority order):

1. **H1B friendliness (weight: 30%)** — No disqualifying language, company on H1B sponsor list
2. **Tech stack match (weight: 30%)** — Python, FastAPI, GCP, ML tools, PyTorch, TensorFlow, etc.
3. **Location (weight: 20%)** — Boston on-site/hybrid = +2 bonus, Remote US = +1, Other = 0
4. **Company tier (weight: 20%)** — On the 250 list = bonus, not on list = flagged but included

### Non-list jobs
Jobs from LinkedIn/Indeed that aren't on the 250 company list are **scored and included** but **flagged as "not on target list"** in the email and UI.

### Duplicate handling
When the same job appears on multiple sources (e.g., LinkedIn + Greenhouse), **keep both but mark as duplicate in the UI**. Dedup is by job URL hash, so different source URLs = different entries with a duplicate flag based on company + title + location match.

---

## 6. Resume Specification

### Source of truth
Google Doc that Easha keeps updated. Pipeline pulls latest at the start of each Step 2 run.

### Structure (fixed order)
1. **Header** — Name, email, phone, location, LinkedIn, GitHub, website (all 6, always)
2. **Education** — Northeastern MS in AI first, VIT B.Tech second
3. **Technical Skills** — Grouped by category (Languages & Frameworks, ML & AI, Cloud & DevOps, Database & Big Data, Tools & Platforms)
4. **Work Experience** — OK AI → TA → Info Edge → Pharmeasy (all 3 work experiences + TA always included, never removed)
5. **Projects & Leadership** — 2 from current resume + max 1 swap

### Tone
Conversational but polished — sounds like a real person, not a template. Professional but warm. Natural verbs (built, designed, created, improved, ran). No AI-generated phrasing.

### Formatting
- **Strictly 1 page max**
- No summary/objective section
- Flexible bullet points: 2-4 per entry, LLM decides based on available space
- Clean, minimal styling (standard fonts, no color accents)
- Visa status: **never mentioned**

### Tailoring rules
- LLM reorders **coursework list** to match JD keywords
- LLM reorders **skills within each category** to put JD-relevant ones first
- LLM rephrases bullet points to mirror JD keywords (truthfully)
- **Section order stays fixed** — Education → Skills → Experience → Projects always

### Project swap rules
- **Always keep both current resume projects** (Bayesian Uncertainty QA, Cricket Shot Recognition)
- **May swap in max 1 additional project** from the pool:
  - **KidneyCare** — primary swap candidate (MIT MedHack, CV pipeline, 96.2% accuracy, FastAPI, FHIR)
  - **Mindful Monitor** — swap in ONLY for health tech roles
- Swapped project replaces nothing — it's added as a 3rd project only if space permits on 1 page, otherwise the least relevant of the 2 existing projects gets condensed to make room

### Work experiences — NEVER REMOVE
All 3 work experiences + TA role must always appear:
- OK AI (ML Intern)
- Khoury College TA (under Experience)
- Info Edge (Senior Software Developer)
- Pharmeasy (Software Developer)

### Metrics (verified rough estimates — LLM may only use these)

**OK AI:**
- 12x performance improvement (60s → 5s response times)
- 50-60 API endpoints built
- 500-1000 users/candidates served
- Migrated 1 microservice to GCP

**TA Role:**
- Supported ~100 students per semester
- 1 lab session per week

**Info Edge (already on resume):**
- 30% reduction in false positives
- 40% reduction in manual review time

**Pharmeasy (already on resume):**
- 200K+ medical records processed monthly
- 25% reduction in processing time
- 15% improvement in medicine mapping accuracy
- 35% reduction in manual review time

**KidneyCare (swap project):**
- 96.2% CV pipeline accuracy
- 6 team members
- Full stack: toilet-mounted camera, CV pipeline, FastAPI backend, InterSystems IRIS FHIR, React frontend

**Mindful Monitor (swap project — health tech only):**
- Hackathon project, describe functionality only, no impact metrics

### Hallucination guardrail
LLM must NOT invent:
- Companies not worked at
- Degrees not earned
- Technologies not listed in the skills section
- Metrics not in the approved list above
- Job titles not held

---

## 7. Cold Email Specification

### Two versions per job
1. **Hiring manager version** — more personal, references specific product/mission
2. **Recruiter version** — more professional, references role fit + qualifications

### Format
- **5 sentences max**
- Lead with genuine interest in the company's product/mission + specific role fit
- No fluff, no "I hope this email finds you well"
- Clear low-pressure ask (15-min chat)
- Sound human, not templated

### Subject line format
`Interested in [Role] — [quick differentiator]`

The differentiator is a concrete detail from Easha's background relevant to the JD. Examples:
- "Interested in ML Engineer — built healthcare CV pipeline at 96% accuracy"
- "Interested in Backend Eng — migrated full platform to GCP, 12x faster"
- "Interested in AI Engineer — Northeastern MS in AI, graduating May 2026"

### Banned phrases (cold emails + resume)
- "leveraged", "spearheaded", "utilized", "orchestrated"
- "passionate about", "thrilled to apply", "excited to bring my expertise"
- "I hope this email finds you well"
- "I believe I would be a great fit"

---

## 8. Cover Letter Specification

**Generate only when the JD explicitly requires a cover letter.**

When generated:
- Same tone as cold emails (conversational, human, specific)
- 3-4 short paragraphs max
- Lead with company interest, connect experience to role, close with enthusiasm
- Follows all banned phrase rules
- Stored in same Google Doc as cold emails

---

## 9. Summary Email Format (Step 1 — Digest)

### Batching
One combined email with all new jobs since last email.

### Fields per job (in this order)
1. Score (out of 10)
2. Job title + company + location
3. Full JD snippet (first 500 chars)
4. Tech stack extracted from JD
5. Link to original listing
6. H1B confidence flag (✅ confirmed sponsor / ⚠️ unknown / ❌ filtered out)

### Sorting
Newest first (most recently posted).

### Additional sections in digest
- **Rate limit monitor:** Warning when Apify credits < 20% or GitHub Actions minutes < 20% remaining
- **Pipeline status:** Any errors from scraping or scoring, with counts
- **Link to web UI** for job selection

---

## 10. Step 2 Completion Notification

When tailoring completes, **both:**
- **Email** with links to all created Google Docs (resume docs + email docs)
- **Web UI update** showing completed status with doc links

---

## 11. Resume & Document Output

### Resume (LaTeX → PDF — primary)
- **Template:** LaTeX template in repo (`templates/resume.tex`), matching current resume style
- **Build:** `latexmk` or `pdflatex` in GitHub Actions (via `texlive-latex-base`)
- **Naming:** `Resume — [Company] — [Role] — [Date].pdf`
- **Storage:** PDF uploaded to Google Drive (shareable link) + committed to repo

### Google Doc (shareable backup)
- **Created alongside PDF** for easy sharing via link
- **Plain text content** (no complex formatting — the PDF is the styled version)
- **Naming:** `Resume — [Company] — [Role] — [Date]`
- **Sharing:** Anyone with link can view

### Cold email doc
- **Naming:** `Cold Emails — [Company] — [Role] — [Date]`
- **Content:** Both versions (hiring manager + recruiter), with subject lines
- **If cover letter generated:** Appended to the same doc

### Markdown backup
- Saved to `output/[date]/[company-role].md` in repo
- Contains: tailored resume + cold emails + cover letter (if any) + job metadata
- **Retained forever**

---

## 12. Web UI Specification

### Hosting
GitHub Pages (free, static site from the repo)

### Security
Client-side password gate (JS). GitHub Actions triggers use a Personal Access Token.

### Features
1. **Browse & select jobs to tailor** — table of scored jobs with checkboxes, "Process Selected" button triggers GitHub Actions workflow_dispatch
2. **Retry failed jobs** — list of jobs where LLM/Docs failed, with retry buttons
3. **Update job status** — dropdown per job: seen → scored → tailored → applied → response → interview → offer → rejected
4. **View past tailored resumes + emails** — links to Google Docs and markdown files
5. **Dashboard** — stats: total scraped, total tailored, total applied, response rate, interview rate, by company/source/week

### Data flow
- UI reads directly from **Supabase** via JS client (supabase-js)
- UI triggers GitHub Actions via API (workflow_dispatch with job IDs)
- Pipeline writes to Supabase after each run
- No `jobs.json` file needed — Supabase is the single source of truth

---

## 13. Storage (Supabase)

### Database
**Supabase free tier** — PostgreSQL, 500MB, REST API, dashboard included.
Accessible from both pipeline (Python via `supabase-py`) and web UI (JS client).

### Table: `jobs`
```sql
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  title TEXT,
  company TEXT,
  url TEXT,
  source TEXT,  -- 'linkedin' | 'indeed' | 'greenhouse' | 'google' | 'ziprecruiter'
  description TEXT,
  location TEXT,
  score REAL,
  h1b_flag TEXT,  -- 'confirmed' | 'unknown' | 'blocked'
  on_target_list BOOLEAN DEFAULT false,
  duplicate_of TEXT,  -- nullable, id of duplicate
  status TEXT DEFAULT 'seen',  -- seen | scored | tailored | applied | response | interview | offer | rejected
  first_seen_at TIMESTAMPTZ DEFAULT now(),
  tailored_at TIMESTAMPTZ,
  applied_at TIMESTAMPTZ,
  resume_pdf_url TEXT,
  doc_url TEXT,
  email_doc_url TEXT,
  md_path TEXT,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### Dedup window
**30 days** — jobs older than 30 days are eligible to resurface.

### Persistence
Supabase handles persistence natively. No artifact juggling needed.

---

## 14. LLM Configuration

### Providers
| Provider | Model | Use case | Free tier |
|----------|-------|----------|-----------|
| Groq | Llama 3.3 70B Versatile | Resume tailoring (primary) | 30 RPM, 14.4K req/day |
| Google Gemini | Gemini 2.0 Flash | Cold emails, scoring, fallback | 15 RPM, 1.5K req/day |

### Fallback logic
If primary provider is rate-limited → fall back to the other. If both fail → log error, mark job for manual retry in UI.

### Temperature
0.3 for all tasks (low creativity, high consistency).

---

## 15. Guardrails (All 4)

### 1. Hallucination detection
Extract company names, school names, specific numbers/metrics from tailored output. Flag anything not present in:
- The master resume (Google Doc)
- The approved metrics list (Section 6)
- The skills section

### 2. Banned phrase filter
Reject output containing:
- "leveraged", "spearheaded", "utilized", "orchestrated"
- "passionate about", "thrilled to apply"

### 3. Keyword match scoring
Extract technical terms from JD (not common words like "team" or "experience"). Calculate percentage that appear in tailored resume. Show score — no hard threshold, informational only.

### 4. Length validation
Resume must not exceed ~3,500 characters (approximately 1 page). Reject and retry if over.

---

## 16. Error Handling

### Critical failures (instant email alert)
- Apify scraper fails (LinkedIn/Indeed down)
- LLM produces garbage (hallucination detected)
- Google Docs API fails (can't create doc)
- GitHub Actions minutes < 20% remaining

### Minor failures (included in digest email)
- Individual job scrape fails
- Single LLM call times out (but others succeed)
- Google Doc sharing permission fails

### Retry strategy
No automatic retry. Failed jobs are **logged and displayed in the web UI** with a manual retry button. User chooses which to retry.

### Rate limit monitoring
At the start of each run, check:
- Apify credit balance → warn in digest if < 20%
- GitHub Actions minutes used this month → warn if < 20% remaining

---

## 17. Resume Source Material

### Personal info
- **Name:** Easha Meher Koppisetty
- **Email:** mehereasha2601@gmail.com
- **Phone:** 8572943442
- **Location:** Boston, MA
- **LinkedIn:** https://www.linkedin.com/in/easha-meher
- **GitHub:** https://github.com/mehereasha2601
- **Website:** https://mehereasha2601.github.io/

### Education
**Northeastern University** — MS in Artificial Intelligence (Jan 2024 – May 2026, Boston, MA)
Coursework: Foundations of AI, Machine Learning, Deep Learning, Natural Language Processing, AI for HCI

**Vellore Institute of Technology** — B.Tech in Computer Science (2017 – 2021, Vellore, India)
Coursework: Database Management Systems, Object-Oriented Programming, Data Analytics, Image Processing

### Technical skills
- **Languages & Frameworks:** Python, Java, C++, JavaScript, React, Flutter, R, HTML, CSS
- **ML & AI:** TensorFlow, PyTorch, Keras, Scikit-learn, OpenCV, SpaCy, NLTK, TorchVision
- **Cloud & DevOps:** AWS (Lambda, S3, DynamoDB), GCP, Azure, Docker, Kubernetes, Jenkins, Linux
- **Database & Big Data:** SQL, MongoDB, BigQuery, Snowflake, PostgreSQL, Kafka, Apache Spark
- **Tools & Platforms:** Git, Copilot, Bitbucket, FastAPI, LangChain, OpenAI API

### Work experience

**OK AI — Machine Learning Intern (Sep 2025 – Jan 2026, Boston, MA)**
- Engineered voice AI interview platform serving frontline workers using MERN stack
- Designed conversational prompts/workflows for multilingual candidate screening
- Architected cloud backend, achieving 12x performance improvement (60s → 5s)
- Built 50-60 API endpoints, serving 500-1000 users/candidates
- Migrated 1 microservice to GCP
- Built secure auth systems and scalable database architecture

**Khoury College — Graduate TA, Object-Oriented Design (Sep 2024 – Aug 2025, Boston, MA)**
- Conducted lab sessions on OOP, Software Design Patterns, System Architecture
- Supported ~100 students/semester, 1 lab session/week
- Graded and provided personalized feedback

**Info Edge — Senior Software Developer (Jul 2023 – Dec 2023, Bangalore, India)**
- Developed AI/ML models to detect cheating in online exams via webcam feeds
- Designed real-time fraud detection with CV + NLP, reducing false positives by 30%
- Built automated monitoring pipelines (Python, OpenCV, TensorFlow)
- Integrated adaptive learning algorithms for dynamic flagging
- Reduced manual review time by 40%

**Pharmeasy — Software Developer (Jul 2021 – Jul 2023, Bangalore, India)**
- Built backend services processing 200K+ medical records/month (Python, Java, PostgreSQL, AWS)
- Designed ETL pipelines and REST APIs, reducing processing time by 25%
- Developed React UI + OCR integration for prescription digitization, +15% accuracy
- Created automated tests (pytest, JUnit), monitoring dashboards, reducing manual review by 35%

### Projects (always on resume)

**Bayesian Uncertainty Quantification in Medical QA Systems (2025)**
- Fine-tuned LLaMA 2, Mistral, BERT on MedQA (50K+ samples), 84% test accuracy
- Monte Carlo Dropout for uncertainty estimation, entropy optimized at 1.13
- LoRA fine-tuning, reducing GPU memory usage by 30%

**Analyzing Cricket: Shot Recognition & Similarity**
- EfficientNetV2 + OpenCV pipeline, 94% accuracy
- MediaPipe Pose Estimation, 1,000+ video frames processed
- TensorRT + ONNX Runtime optimization, 35% inference speed improvement

### Projects (swap pool — max 1 swap-in)

**KidneyCare — MIT MedHack (2026) [PRIMARY SWAP]**
- Toilet-mounted camera, computer vision pipeline, FastAPI backend
- InterSystems IRIS FHIR server (SQLite fallback), React frontend via Lovable
- 96.2% CV pipeline accuracy, 6-person team
- Passive kidney health monitoring through urine foam analysis

**Mindful Monitor [HEALTH TECH ROLES ONLY]**
- Stress-relief EEG companion app (React, TypeScript, Lovable, Cursor)
- Hackathon project — describe functionality only, no impact metrics

---

## 18. Project Structure

```
job-hunter/
├── .github/
│   └── workflows/
│       ├── scrape_greenhouse.yml    # Every 30 min, weekdays
│       ├── scrape_jobspy.yml        # Every 2 hrs, weekdays (Indeed/Google/Zip/LinkedIn)
│       ├── scrape_apify.yml         # Every 2 hrs, weekdays (LinkedIn fallback)
│       ├── process_step1.yml        # 3x/day (noon, 3pm, 6pm)
│       └── process_step2.yml        # On-demand (workflow_dispatch)
├── src/
│   ├── config.py                    # All configuration
│   ├── main_scrape.py               # Scraping orchestrator
│   ├── main_score.py                # Scoring + digest email
│   ├── main_tailor.py               # Tailoring + doc creation
│   ├── scraper_greenhouse.py        # Greenhouse JSON API scraper
│   ├── scraper_jobspy.py            # JobSpy wrapper (Indeed/Google/Zip/LinkedIn)
│   ├── scraper_apify.py             # Apify LinkedIn fallback
│   ├── db.py                        # Supabase client + queries
│   ├── scorer.py                    # LLM relevance scoring
│   ├── h1b_filter.py                # H1B keyword filter
│   ├── llm.py                       # Groq + Gemini clients
│   ├── resume_tailor.py             # Resume generation
│   ├── latex_builder.py             # LaTeX template → PDF
│   ├── email_drafter.py             # Cold email + cover letter
│   ├── guardrails.py                # All 4 guardrails
│   ├── google_docs.py               # Google Doc creation (plain text backup)
│   ├── notifier.py                  # Gmail SMTP
│   ├── rate_monitor.py              # Apify + GH Actions limits
│   └── output.py                    # Markdown backup
├── templates/
│   └── resume.tex                   # LaTeX resume template
├── ui/
│   ├── index.html                   # Web UI (GitHub Pages)
│   ├── app.js                       # UI logic + Supabase client
│   └── style.css                    # UI styling
├── tests/
│   ├── test_harness.py              # Phase 1: LLM output quality testing
│   ├── test_jobs.json               # Sample job listings for testing
│   └── test_guardrails.py           # Guardrail unit tests
├── output/                          # Markdown backups (by date)
├── resume.txt                       # Fallback resume (plain text)
├── requirements.txt
└── README.md
```

---

## 19. Setup Requirements

### GitHub Secrets
- `APIFY_TOKEN` — from apify.com (LinkedIn fallback only)
- `GROQ_API_KEY` — from console.groq.com
- `GEMINI_API_KEY` — from aistudio.google.com
- `GOOGLE_CREDENTIALS_JSON` — service account JSON (Docs/Drive)
- `GMAIL_APP_PASSWORD` — Gmail app password
- `NOTIFICATION_EMAIL` — Gmail address
- `RESUME_GOOGLE_DOC_ID` — Master resume doc ID
- `SUPABASE_URL` — from Supabase project settings
- `SUPABASE_KEY` — Supabase anon/service key
- `UI_PASSWORD` — Password for web UI
- `GH_PAT` — Personal Access Token for UI → Actions triggers

### External accounts needed
- Supabase (free tier — 500MB PostgreSQL, REST API, dashboard)
- Apify (free tier — LinkedIn fallback only, ~$2-3/month usage)
- Groq (free tier)
- Google AI Studio / Gemini (free tier)
- Google Cloud (service account for Docs/Drive API)
- Gmail (app password)

### Additional dependencies
- `texlive-latex-base` (installed in GitHub Actions for LaTeX → PDF)
- `python-jobspy` (pip, for Indeed/Google/Zip scraping)

---

## 20. Build Order

### Phase 1: Test harness (build first, validate LLM quality)
1. Local test script with 3-5 real job listings
2. Side-by-side Groq vs Gemini output comparison
3. All 4 guardrails running on test output
4. LaTeX template creation + PDF generation test
5. Iterate on prompts until output quality is good

### Phase 2: Core pipeline
6. Greenhouse scraper (custom JSON API)
7. JobSpy wrapper (Indeed/Google/Zip/LinkedIn)
8. Apify LinkedIn fallback
9. Supabase client + schema setup
10. H1B filter
11. LLM scorer
12. Resume tailor + LaTeX builder
13. Cold email drafter
14. Cover letter generator (conditional)
15. Google Docs creation (plain text backup)
16. Gmail SMTP notifier
17. Rate limit monitor
18. Markdown output

### Phase 3: Orchestration
19. GitHub Actions workflows (all 5 — greenhouse, jobspy, apify, step1, step2)
20. Supabase as shared state between pipeline + UI
21. Step 2 workflow_dispatch trigger

### Phase 4: Web UI
22. Supabase JS client integration
23. Job selection interface
24. Retry failed jobs
25. Status tracking (applied → interview → offer pipeline)
26. Past resumes/emails viewer
27. Dashboard with stats
28. Password protection

### Phase 5: Go live
29. End-to-end test with real data
30. Monitor first week of runs
31. Iterate on prompts based on real output