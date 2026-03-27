"""
Supabase database client.
Handles all database operations for job storage and tracking.
Schema from Section 13 of spec.md.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.config import Config
import hashlib
import requests


class Database:
    """Supabase database client using direct REST API calls."""
    
    def __init__(self):
        """Initialize Supabase REST API client."""
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        
        self.base_url = f"{Config.SUPABASE_URL}/rest/v1"
        self.headers = {
            'apikey': Config.SUPABASE_KEY,
            'Authorization': f'Bearer {Config.SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def _query(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make REST API request."""
        url = f"{self.base_url}/{endpoint}"
        
        # Merge custom headers if provided
        headers = {**self.headers}
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    
    @staticmethod
    def generate_job_id(url: str, company: str, title: str) -> str:
        """Generate deterministic job ID from URL (primary) or company+title."""
        if url:
            return hashlib.md5(url.encode()).hexdigest()
        else:
            key = f"{company}_{title}".lower().replace(' ', '_')
            return hashlib.md5(key.encode()).hexdigest()
    
    def insert_job(self, job: Dict) -> Dict:
        """
        Insert a new job or update existing.
        
        Args:
            job: Dict with job details (title, company, url, source, description, location, date_posted)
        
        Returns:
            Inserted/updated job record
        """
        job_id = self.generate_job_id(
            job.get('url', ''),
            job.get('company', ''),
            job.get('title', '')
        )
        
        # Check if exists
        existing = self.get_job(job_id)
        
        if existing:
            # Update updated_at timestamp
            response = self._query(
                'PATCH',
                f'jobs?id=eq.{job_id}',
                json={'updated_at': datetime.now().isoformat()}
            )
            return existing
        
        # Insert new
        job_data = {
            'id': job_id,
            'title': job.get('title'),
            'company': job.get('company'),
            'url': job.get('url'),
            'source': job.get('source'),
            'description': job.get('description'),
            'location': job.get('location'),
            'date_posted': job.get('date_posted'),
            'h1b_flag': job.get('h1b_flag', 'unknown'),
            'on_target_list': job.get('on_target_list', False),
            'status': 'seen'
        }
        
        response = self._query('POST', 'jobs', json=job_data)
        data = response.json()
        return data[0] if data else None
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID."""
        try:
            response = self._query('GET', f'jobs?id=eq.{job_id}&select=*')
            data = response.json()
            return data[0] if data else None
        except requests.exceptions.HTTPError:
            return None
    
    def get_unscored_jobs(self) -> List[Dict]:
        """Get jobs that need scoring (status='seen', score=null)."""
        response = self._query('GET', 'jobs?status=eq.seen&score=is.null&select=*')
        return response.json() or []
    
    def update_job_score(self, job_id: str, score: float, h1b_flag: str) -> Dict:
        """Update job with relevance score."""
        response = self._query(
            'PATCH',
            f'jobs?id=eq.{job_id}',
            json={
                'score': score,
                'h1b_flag': h1b_flag,
                'status': 'scored',
                'updated_at': datetime.now().isoformat()
            }
        )
        data = response.json()
        return data[0] if data else None
    
    def get_scored_jobs(self, min_score: float = 7.0, limit: int = 50) -> List[Dict]:
        """Get jobs scored above threshold, for digest email."""
        response = self._query(
            'GET',
            f'jobs?status=eq.scored&score=gte.{min_score}&order=first_seen_at.desc&limit={limit}&select=*'
        )
        return response.json() or []
    
    def get_jobs_to_tailor(self, job_ids: List[str]) -> List[Dict]:
        """Get specific jobs by IDs for tailoring."""
        # Build OR query for multiple IDs
        ids_param = ','.join(f'"{jid}"' for jid in job_ids)
        response = self._query('GET', f'jobs?id=in.({ids_param})&select=*')
        return response.json() or []
    
    def update_job_tailored(
        self,
        job_id: str,
        resume_pdf_url: str,
        doc_url: str,
        email_doc_url: str,
        md_path: str
    ) -> Dict:
        """Update job with tailored output links."""
        response = self._query(
            'PATCH',
            f'jobs?id=eq.{job_id}',
            json={
                'status': 'tailored',
                'tailored_at': datetime.now().isoformat(),
                'resume_pdf_url': resume_pdf_url,
                'doc_url': doc_url,
                'email_doc_url': email_doc_url,
                'md_path': md_path,
                'updated_at': datetime.now().isoformat()
            }
        )
        data = response.json()
        return data[0] if data else None
    
    def update_job_status(self, job_id: str, status: str) -> Dict:
        """
        Update job status.
        Status: seen | scored | tailored | applied | response | interview | offer | rejected
        """
        data = {
            'status': status,
            'updated_at': datetime.now().isoformat()
        }
        
        if status == 'applied':
            data['applied_at'] = datetime.now().isoformat()
        
        response = self._query('PATCH', f'jobs?id=eq.{job_id}', json=data)
        result = response.json()
        return result[0] if result else None
    
    def mark_job_error(self, job_id: str, error: str) -> Dict:
        """Mark job with error for manual retry."""
        response = self._query(
            'PATCH',
            f'jobs?id=eq.{job_id}',
            json={'error': error, 'updated_at': datetime.now().isoformat()}
        )
        data = response.json()
        return data[0] if data else None
    
    def get_recent_jobs(self, days: int = 7) -> List[Dict]:
        """Get jobs from last N days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        response = self._query(
            'GET',
            f'jobs?first_seen_at=gte.{cutoff}&order=first_seen_at.desc&select=*'
        )
        return response.json() or []
    
    def find_duplicates(self, company: str, title: str, location: str) -> List[Dict]:
        """Find potential duplicate jobs by company + title + location."""
        # URL encode parameters
        import urllib.parse
        company_enc = urllib.parse.quote(company)
        title_enc = urllib.parse.quote(title)
        location_enc = urllib.parse.quote(location)
        
        response = self._query(
            'GET',
            f'jobs?company=eq.{company_enc}&title=eq.{title_enc}&location=eq.{location_enc}&select=*'
        )
        return response.json() or []
    
    def mark_duplicate(self, job_id: str, duplicate_of: str) -> Dict:
        """Mark job as duplicate of another job."""
        response = self._query(
            'PATCH',
            f'jobs?id=eq.{job_id}',
            json={'duplicate_of': duplicate_of, 'updated_at': datetime.now().isoformat()}
        )
        data = response.json()
        return data[0] if data else None
    
    def cleanup_old_jobs(self, days: int = 30):
        """Delete jobs older than N days (dedup window)."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        response = self._query('DELETE', f'jobs?first_seen_at=lt.{cutoff}')
        data = response.json()
        return len(data) if data else 0


# SQL Schema for reference (run manually in Supabase dashboard)
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  title TEXT,
  company TEXT,
  url TEXT,
  source TEXT,  -- 'linkedin' | 'indeed' | 'greenhouse' | 'google' | 'ziprecruiter'
  description TEXT,
  location TEXT,
  date_posted TIMESTAMPTZ,  -- When the job was originally posted by company
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

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(score);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_first_seen ON jobs(first_seen_at);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON jobs(date_posted);
"""
