# Phase 4: Web UI Dashboard - Build Plan

**Start Date:** March 26, 2026  
**Phase:** 4 of 5  
**Goal:** Build a modern web interface for browsing jobs, triggering tailoring, and tracking applications

---

## Overview

Based on spec.md Section 12 (Web UI Specification), we need to build a web dashboard that:
- Provides a modern UI for browsing scored jobs
- Allows one-click tailoring via GitHub Actions
- Tracks application status through the pipeline
- Shows past generated resumes and emails
- Displays pipeline statistics and metrics

---

## Architecture

### Tech Stack
- **Backend:** FastAPI (Python) - REST API server
- **Frontend:** React + Vite - Modern SPA
- **Database:** Supabase (existing) - Direct JS client access
- **Auth:** Simple password protection (UI_PASSWORD env var)
- **Deployment:** 
  - Backend: Can run locally or on a simple hosting service
  - Frontend: GitHub Pages (static site)

### Data Flow
```
User → React UI → Supabase (read jobs)
             ↓
          GitHub Actions API (trigger tailoring)
             ↓
          Pipeline → Supabase (write results)
             ↓
          React UI (poll for updates)
```

---

## Components to Build

### 1. Backend API (FastAPI)

**File:** `api/main.py`

**Endpoints:**
- `GET /api/jobs` - List all jobs with filters
  - Query params: `status`, `min_score`, `company`, `source`, `limit`, `offset`
- `GET /api/jobs/{job_id}` - Get single job details
- `POST /api/jobs/{job_id}/status` - Update job status
- `GET /api/stats` - Get dashboard statistics
- `POST /api/tailor` - Trigger GitHub Actions tailoring workflow
  - Body: `{"job_ids": ["id1", "id2"]}`
- `GET /api/outputs` - List past generated outputs
- `GET /api/health` - Health check

**Features:**
- CORS enabled for frontend
- Password middleware (checks `UI_PASSWORD`)
- Direct Supabase integration
- GitHub API integration for workflow triggers

### 2. Frontend (React)

**Structure:**
```
ui/
├── src/
│   ├── App.jsx              # Main app component
│   ├── components/
│   │   ├── Login.jsx        # Password gate
│   │   ├── JobTable.jsx     # Browsable job list
│   │   ├── JobCard.jsx      # Individual job display
│   │   ├── Dashboard.jsx    # Stats dashboard
│   │   ├── StatusDropdown.jsx  # Status update
│   │   ├── OutputsViewer.jsx   # Past resumes/emails
│   │   └── Header.jsx       # Navigation
│   ├── api.js               # API client
│   ├── supabase.js          # Supabase client
│   └── main.jsx             # Entry point
├── index.html
├── package.json
└── vite.config.js
```

**Pages/Views:**
1. **Login** - Password gate
2. **Jobs** - Browse and select jobs for tailoring
3. **Dashboard** - Statistics and metrics
4. **Outputs** - View past generated content
5. **Retry** - Retry failed jobs

**Key Features:**
- Modern, responsive design (Tailwind CSS)
- Real-time status updates
- Sortable, filterable table
- Checkbox selection for bulk tailoring
- One-click "Tailor Selected" button
- Status badges (color-coded)
- Score display with visual indicators

### 3. Authentication

**Implementation:**
- Simple password check on first load
- Store auth token in localStorage
- Middleware on backend checks password
- No user accounts - single password for personal use

### 4. GitHub Actions Integration

**Functionality:**
- Trigger Step 2 workflow via GitHub API
- Use `GH_PAT` (Personal Access Token) from config
- Pass selected job IDs as workflow inputs
- Show loading state while processing
- Poll for completion

---

## Database Schema (Existing)

Already built in Phase 2:
```sql
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  title TEXT,
  company TEXT,
  url TEXT,
  source TEXT,
  description TEXT,
  location TEXT,
  score REAL,
  h1b_flag TEXT,
  on_target_list BOOLEAN,
  duplicate_of TEXT,
  status TEXT DEFAULT 'seen',
  first_seen_at TIMESTAMPTZ,
  tailored_at TIMESTAMPTZ,
  applied_at TIMESTAMPTZ,
  resume_pdf_url TEXT,
  doc_url TEXT,
  email_doc_url TEXT,
  md_path TEXT,
  error TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

---

## Features Breakdown

### Feature 1: Browse & Select Jobs ⭐ Priority
**What:** Table of all scored jobs with checkboxes
**Details:**
- Show: title, company, location, score, status, H1B flag
- Filter by: status, score range, company
- Sort by: score, date, company
- Select multiple via checkboxes
- "Tailor Selected" button → triggers GitHub Actions

### Feature 2: Job Details Modal
**What:** Click job row to see full details
**Details:**
- Full job description
- Tech stack keywords extracted
- Score breakdown
- Original listing link
- H1B status explanation

### Feature 3: Status Tracking
**What:** Dropdown to update status per job
**Details:**
- States: seen → scored → tailored → applied → response → interview → offer → rejected
- Auto-updates `updated_at` timestamp
- Shows transition history

### Feature 4: Dashboard Stats
**What:** Overview of pipeline metrics
**Details:**
- Total jobs scraped
- Total jobs scored
- Total jobs tailored
- Total applied
- Response rate (%)
- Interview rate (%)
- Charts: by company, by source, by week

### Feature 5: Past Outputs Viewer
**What:** Browse previously generated resumes/emails
**Details:**
- List of tailored jobs
- Links to Google Docs
- Links to markdown files in repo
- Download buttons
- Timestamp and company info

### Feature 6: Retry Failed Jobs
**What:** List of jobs with errors, retry button
**Details:**
- Show error message
- "Retry" button re-triggers tailoring
- Clear error on success

---

## Implementation Steps

### Step 1: Backend API Setup ✅ (First)
1. Create `api/` directory structure
2. Set up FastAPI with dependencies
3. Build Supabase client integration
4. Implement authentication middleware
5. Create all REST endpoints
6. Test with curl/Postman

### Step 2: Frontend Foundation
1. Set up Vite + React project
2. Configure Tailwind CSS
3. Create basic routing
4. Implement login page
5. Set up API client

### Step 3: Core Features
1. Build JobTable component
2. Add filtering and sorting
3. Implement job selection
4. Create "Tailor Selected" flow
5. Add status updates

### Step 4: Dashboard & Stats
1. Implement stats calculations
2. Build dashboard UI
3. Add charts (simple bar/line charts)

### Step 5: Outputs Viewer
1. List past tailored jobs
2. Show links to docs
3. Display markdown content

### Step 6: Testing & Deployment
1. Test all features locally
2. Build frontend for production
3. Deploy to GitHub Pages
4. Document deployment process

---

## Dependencies

### Backend (`api/requirements.txt`)
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
supabase>=2.0.0
python-dotenv>=1.0.0
httpx>=0.25.0  # For GitHub API
```

### Frontend (`ui/package.json`)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@supabase/supabase-js": "^2.38.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

---

## File Structure

```
job-hunter/
├── api/                          # Backend API
│   ├── main.py                   # FastAPI app
│   ├── auth.py                   # Authentication
│   ├── github_client.py          # GitHub Actions trigger
│   ├── requirements.txt
│   └── README.md
├── ui/                           # Frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── api.js
│   │   └── main.jsx
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── src/                          # Existing pipeline code
├── .github/workflows/            # Existing workflows
└── README.md
```

---

## Environment Variables

### Backend (`.env`)
```bash
# Existing
SUPABASE_URL=...
SUPABASE_KEY=...
GROQ_API_KEY=...
GEMINI_API_KEY=...

# New for Phase 4
UI_PASSWORD=your-secure-password
GH_PAT=github_pat_...  # Personal Access Token for triggering workflows
```

### Frontend (`ui/.env`)
```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
VITE_GITHUB_REPO=mehereasha2601/Job-Hunter
```

---

## Design Mockup (Text)

```
┌─────────────────────────────────────────────────────────────┐
│  Job Hunter Dashboard                    [Dashboard] [Jobs]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📊 Stats: 124 scraped | 89 scored | 12 tailored | 5 applied│
│                                                               │
│  Filter: [Status ▼] [Min Score: 7] [Company: _____]         │
│                                                               │
│  [☐] Score  Company      Role              Location  Status  │
│  ──────────────────────────────────────────────────────────  │
│  [☐] 10.0   Klaviyo      Full Stack Eng    Boston    scored  │
│  [☐]  9.0   Scale AI     AI/ML Engineer    SF        scored  │
│  [☐]  9.0   Databricks   Backend Eng       Remote    scored  │
│  [☐]  7.0   Stripe       Sr Backend        Remote    scored  │
│                                                               │
│  [Tailor Selected (0)]  [View All Outputs]                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

✅ User can log in with password
✅ User can browse all jobs in a table
✅ User can filter by status, score, company
✅ User can select multiple jobs
✅ User can trigger tailoring for selected jobs
✅ User can see tailoring progress/status
✅ User can update job status (applied, interview, etc.)
✅ User can view past generated resumes/emails
✅ Dashboard shows accurate statistics
✅ UI is responsive and modern-looking
✅ All features work end-to-end

---

## Timeline Estimate

- **Backend API:** 2-3 hours
- **Frontend Setup:** 1 hour
- **Job Table & Selection:** 2 hours
- **Dashboard Stats:** 1-2 hours
- **Outputs Viewer:** 1 hour
- **Testing & Polish:** 1-2 hours

**Total:** ~8-11 hours of focused work

---

## Phase 4 Deliverables

1. FastAPI backend with 7 REST endpoints
2. React frontend with 4 main views
3. Password authentication
4. Job browsing and selection interface
5. One-click tailoring trigger
6. Status tracking system
7. Dashboard with statistics
8. Past outputs viewer
9. Responsive, modern UI
10. Complete documentation

---

**Status:** Ready to begin implementation
**Next:** Build FastAPI backend first, then React frontend
