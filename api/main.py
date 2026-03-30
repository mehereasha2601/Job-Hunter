"""
FastAPI backend for Job Hunter Web UI.
Provides REST API for job browsing, status updates, and tailoring triggers.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import os
import httpx

# Import existing modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import Database
from src.config import Config

app = FastAPI(
    title="Job Hunter API",
    description="Backend API for automated job hunting pipeline",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple password authentication
security = HTTPBasic()


def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify UI password."""
    correct_password = Config.UI_PASSWORD or "changeme"
    if credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Pydantic models
class JobStatusUpdate(BaseModel):
    status: str  # seen, scored, tailored, applied, response, interview, offer, rejected


class TailorRequest(BaseModel):
    job_ids: List[str]


class StatsResponse(BaseModel):
    total_scraped: int
    total_scored: int
    total_tailored: int
    total_applied: int
    by_company: Dict[str, int]
    by_source: Dict[str, int]
    by_status: Dict[str, int]


# Initialize database
db = Database()


def _parse_content_range_total(content_range: Optional[str]) -> Optional[int]:
    """Parse PostgREST Content-Range header: '0-24/317' -> 317."""
    if not content_range:
        return None
    parts = content_range.split("/")
    if len(parts) != 2:
        return None
    total = parts[1].strip()
    if total == "*":
        return None
    try:
        return int(total)
    except ValueError:
        return None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Job Hunter API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        jobs = db.get_recent_jobs(days=1)
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/api/jobs")
async def list_jobs(
    status_filter: Optional[str] = Query(None, alias="status"),
    min_score: Optional[float] = Query(None, ge=0, le=10),
    company: Optional[str] = None,
    source: Optional[str] = None,
    sort_by: str = Query("score", regex="^(score|date_posted|first_seen_at)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    full_time_only: bool = Query(
        True,
        description="Exclude non-full-time titles (intern, co-op, part-time, etc.)",
    ),
    _: str = Depends(verify_password)
):
    """
    List all jobs with optional filters.
    
    Filters:
    - status: Filter by job status
    - min_score: Minimum score threshold
    - company: Filter by company name (case-insensitive partial match)
    - source: Filter by job source
    - sort_by: Sort field (score, date_posted, first_seen_at) - defaults to score
    - limit: Maximum number of results
    - offset: Pagination offset
    - full_time_only: When true, drop rows whose title matches intern/co-op/part-time patterns
      (applied after fetch; Content-Range total may include excluded rows).
    """
    try:
        # Build query parameters
        params = []
        params.append(f'select=*')
        
        # Apply filters
        if status_filter:
            params.append(f'status=eq.{status_filter}')
        if min_score is not None:
            params.append(f'score=gte.{min_score}')
        if company:
            import urllib.parse
            company_enc = urllib.parse.quote(f'%{company}%')
            params.append(f'company=ilike.{company_enc}')
        if source:
            params.append(f'source=eq.{source}')
        
        # Sorting
        if sort_by == "date_posted":
            params.append('order=date_posted.desc.nullslast,score.desc')
        elif sort_by == "first_seen_at":
            params.append('order=first_seen_at.desc')
        else:  # Default: score
            params.append('order=score.desc.nullslast,date_posted.desc.nullslast')
        
        # Pagination
        end_range = offset + limit - 1
        
        # Build URL
        query_string = '&'.join(params)
        response = db._query('GET', f'jobs?{query_string}', headers={
            **db.headers,
            'Range': f'{offset}-{end_range}',
            'Prefer': 'count=exact',
        })
        
        jobs = response.json()
        total = _parse_content_range_total(response.headers.get("Content-Range"))

        if full_time_only:
            jobs = [
                j
                for j in jobs
                if not Config.title_is_non_fulltime(j.get("title", ""))
            ]

        return {
            "jobs": jobs,
            "count": len(jobs),
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, _: str = Depends(verify_password)):
    """Get single job by ID."""
    try:
        job = db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job: {str(e)}")


@app.patch("/api/jobs/{job_id}/status")
async def update_job_status(
    job_id: str,
    update: JobStatusUpdate,
    _: str = Depends(verify_password)
):
    """Update job status."""
    valid_statuses = ['seen', 'scored', 'tailored', 'applied', 'response', 'interview', 'offer', 'rejected']
    
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    try:
        # Update status in database
        updated_job = db.update_job_status(job_id, update.status)
        
        if not updated_job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "job_id": job_id,
            "status": update.status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@app.get("/api/stats")
async def get_stats(_: str = Depends(verify_password)) -> StatsResponse:
    """Get dashboard statistics."""
    try:
        # Fetch all jobs
        jobs = db.get_recent_jobs(days=365)  # Get all jobs from last year
        
        # Calculate stats
        total_scraped = len(jobs)
        total_scored = len([j for j in jobs if j.get('score')])
        total_tailored = len([j for j in jobs if j.get('status') == 'tailored' or j.get('tailored_at')])
        total_applied = len([j for j in jobs if j.get('status') in ['applied', 'response', 'interview', 'offer']])
        
        # Group by company
        by_company = {}
        for job in jobs:
            company = job.get('company', 'Unknown')
            by_company[company] = by_company.get(company, 0) + 1
        
        # Group by source
        by_source = {}
        for job in jobs:
            source = job.get('source', 'unknown')
            by_source[source] = by_source.get(source, 0) + 1
        
        # Group by status
        by_status = {}
        for job in jobs:
            status = job.get('status', 'seen')
            by_status[status] = by_status.get(status, 0) + 1
        
        return StatsResponse(
            total_scraped=total_scraped,
            total_scored=total_scored,
            total_tailored=total_tailored,
            total_applied=total_applied,
            by_company=by_company,
            by_source=by_source,
            by_status=by_status
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/api/tailor")
async def trigger_tailoring(
    request: TailorRequest,
    _: str = Depends(verify_password)
):
    """
    Trigger GitHub Actions workflow to tailor resumes for selected jobs.
    """
    if not request.job_ids:
        raise HTTPException(status_code=400, detail="No job IDs provided")
    
    if len(request.job_ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 jobs per tailoring batch")
    
    try:
        # Verify all jobs exist
        for job_id in request.job_ids:
            job = db.get_job(job_id)
            if not job:
                raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        # Trigger GitHub Actions workflow
        github_token = Config.GH_PAT
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token not configured")
        
        # GitHub API endpoint for workflow dispatch
        repo = "mehereasha2601/Job-Hunter"  # From your repo
        workflow_id = "step2_tailor.yml"
        
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
        
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "ref": "main",
            "inputs": {
                "job_ids": ",".join(request.job_ids)
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
        
        if response.status_code == 204:
            return {
                "success": True,
                "message": f"Tailoring triggered for {len(request.job_ids)} job(s)",
                "job_ids": request.job_ids,
                "workflow": "step2_tailor"
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"GitHub API error: {response.text}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger tailoring: {str(e)}")


@app.get("/api/outputs")
async def list_outputs(_: str = Depends(verify_password)):
    """List all tailored jobs with output links."""
    try:
        # Build query for tailored jobs
        response = db._query('GET', 'jobs?tailored_at=not.is.null&order=tailored_at.desc&select=*')
        jobs_data = response.json()
        
        tailored_jobs = []
        for job in jobs_data:
            tailored_jobs.append({
                "id": job['id'],
                "title": job['title'],
                "company": job['company'],
                "tailored_at": job['tailored_at'],
                "resume_pdf_url": job.get('resume_pdf_url'),
                "doc_url": job.get('doc_url'),
                "email_doc_url": job.get('email_doc_url'),
                "md_path": job.get('md_path'),
                "status": job['status']
            })
        
        return {
            "outputs": tailored_jobs,
            "count": len(tailored_jobs)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch outputs: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
