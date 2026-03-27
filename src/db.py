"""
Supabase database client.
Handles all database operations for job storage and tracking.
Schema from Section 13 of spec.md.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from supabase import create_client, Client
from src.config import Config
import hashlib


class Database:
    """Supabase database client for job storage and tracking."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")
        
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
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
            result = self.client.table('jobs').update({
                'updated_at': datetime.now().isoformat()
            }).eq('id', job_id).execute()
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
            'date_posted': job.get('date_posted'),  # NEW - original posting date
            'h1b_flag': job.get('h1b_flag', 'unknown'),
            'on_target_list': job.get('on_target_list', False),
            'status': 'seen'
        }
        
        result = self.client.table('jobs').insert(job_data).execute()
        return result.data[0] if result.data else None
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID."""
        result = self.client.table('jobs').select('*').eq('id', job_id).execute()
        return result.data[0] if result.data else None
    
    def get_unscored_jobs(self) -> List[Dict]:
        """Get jobs that need scoring (status='seen', score=null)."""
        result = self.client.table('jobs').select('*').eq('status', 'seen').is_('score', 'null').execute()
        return result.data or []
    
    def update_job_score(self, job_id: str, score: float, h1b_flag: str) -> Dict:
        """Update job with relevance score."""
        result = self.client.table('jobs').update({
            'score': score,
            'h1b_flag': h1b_flag,
            'status': 'scored',
            'updated_at': datetime.now().isoformat()
        }).eq('id', job_id).execute()
        return result.data[0] if result.data else None
    
    def get_scored_jobs(self, min_score: float = 7.0, limit: int = 50) -> List[Dict]:
        """Get jobs scored above threshold, for digest email."""
        result = self.client.table('jobs').select('*').eq('status', 'scored').gte('score', min_score).order('first_seen_at', desc=True).limit(limit).execute()
        return result.data or []
    
    def get_jobs_to_tailor(self, job_ids: List[str]) -> List[Dict]:
        """Get specific jobs by IDs for tailoring."""
        result = self.client.table('jobs').select('*').in_('id', job_ids).execute()
        return result.data or []
    
    def update_job_tailored(
        self,
        job_id: str,
        resume_pdf_url: str,
        doc_url: str,
        email_doc_url: str,
        md_path: str
    ) -> Dict:
        """Update job with tailored output links."""
        result = self.client.table('jobs').update({
            'status': 'tailored',
            'tailored_at': datetime.now().isoformat(),
            'resume_pdf_url': resume_pdf_url,
            'doc_url': doc_url,
            'email_doc_url': email_doc_url,
            'md_path': md_path,
            'updated_at': datetime.now().isoformat()
        }).eq('id', job_id).execute()
        return result.data[0] if result.data else None
    
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
        
        result = self.client.table('jobs').update(data).eq('id', job_id).execute()
        return result.data[0] if result.data else None
    
    def mark_job_error(self, job_id: str, error: str) -> Dict:
        """Mark job with error for manual retry."""
        result = self.client.table('jobs').update({
            'error': error,
            'updated_at': datetime.now().isoformat()
        }).eq('id', job_id).execute()
        return result.data[0] if result.data else None
    
    def get_recent_jobs(self, days: int = 7) -> List[Dict]:
        """Get jobs from last N days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        result = self.client.table('jobs').select('*').gte('first_seen_at', cutoff).order('first_seen_at', desc=True).execute()
        return result.data or []
    
    def find_duplicates(self, company: str, title: str, location: str) -> List[Dict]:
        """Find potential duplicate jobs by company + title + location."""
        result = self.client.table('jobs').select('*').eq('company', company).eq('title', title).eq('location', location).execute()
        return result.data or []
    
    def mark_duplicate(self, job_id: str, duplicate_of: str) -> Dict:
        """Mark job as duplicate of another job."""
        result = self.client.table('jobs').update({
            'duplicate_of': duplicate_of,
            'updated_at': datetime.now().isoformat()
        }).eq('id', job_id).execute()
        return result.data[0] if result.data else None
    
    def cleanup_old_jobs(self, days: int = 30):
        """Delete jobs older than N days (dedup window)."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        result = self.client.table('jobs').delete().lt('first_seen_at', cutoff).execute()
        return len(result.data) if result.data else 0


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
