"""
Apify Google Jobs scraper wrapper.
Uses Apify's Google Jobs Scraper actor (Section 11 of spec.md).
"""

from typing import List, Dict
from datetime import datetime
from apify_client import ApifyClient

from .config import Config


class ApifyScraper:
    """Wrapper for Apify Google Jobs Scraper."""
    
    def __init__(self, api_token: str):
        """
        Initialize Apify scraper.
        
        Args:
            api_token: Apify API token
        """
        self.client = ApifyClient(api_token)
        self.actor_id = 'igview-owner/google-jobs-scraper'
    
    def run_scraper(
        self,
        queries: List[str],
        max_results_per_query: int = 100
    ) -> List[Dict]:
        """
        Run Google Jobs scraper actor.
        
        Args:
            queries: List of search queries (e.g., "Software Engineer Boston")
            max_results_per_query: Max results per query (not used, actor returns ~10 per query)
        
        Returns:
            List of filtered job dicts
        """
        all_jobs = []
        
        for query in queries:
            try:
                # Build actor input
                actor_input = {
                    'query': query,
                    'country': 'us',
                    'datePosted': 'today',  # Last 24 hours for LinkedIn/Google Jobs
                    'page': 1
                }
                
                print(f"Running Apify actor for: {query}...")
                
                # Run actor and wait for results
                run = self.client.actor(self.actor_id).call(run_input=actor_input)
                
                # Fetch results from dataset
                raw_jobs = []
                for item in self.client.dataset(run['defaultDatasetId']).iterate_items():
                    raw_jobs.append(item)
                
                # Normalize and filter
                filtered_count = 0
                for raw_job in raw_jobs:
                    normalized = self.normalize_job(raw_job)
                    
                    if self._should_include_job(normalized):
                        all_jobs.append(normalized)
                        filtered_count += 1
                
                print(f"  Found {len(raw_jobs)} jobs, filtered to {filtered_count}")
            
            except Exception as e:
                print(f"  Error for query '{query}': {e}")
        
        return all_jobs
    
    def normalize_job(self, job: Dict) -> Dict:
        """
        Normalize Apify Google Jobs output to standard format.
        
        Args:
            job: Raw job dict from Apify (igview-owner/google-jobs-scraper)
        
        Returns:
            Normalized job dict
        """
        return {
            'title': job.get('jobTitle', ''),
            'company': job.get('employerName', ''),
            'url': job.get('jobApplyLink', ''),
            'source': f"google ({job.get('jobPublisher', 'unknown')})",
            'description': job.get('jobDescription', ''),
            'location': job.get('jobLocation', ''),
            'raw_data': job
        }
    
    def _should_include_job(self, job: Dict) -> bool:
        """
        Check if job meets filtering criteria (same as Greenhouse).
        
        Filters:
        - Job title match
        - US location (exclude Canada-only, international)
        - Exclude senior roles
        - Exclude manager roles
        - Posted within last 14 days
        """
        title = job.get('title', '').lower()
        location = job.get('location', '').lower()
        raw_data = job.get('raw_data', job)
        
        # 1. Check job title matches
        title_match = any(
            target.lower() in title
            for target in Config.JOB_TITLES
        )
        if not title_match:
            return False
        
        # 2. Exclude senior roles
        is_senior = any(
            keyword.lower() in title
            for keyword in Config.EXCLUDE_SENIORITY_KEYWORDS
        )
        if is_senior:
            return False
        
        # 3. Location filtering (multi-location logic)
        has_us = any(
            keyword in location
            for keyword in Config.US_LOCATION_KEYWORDS
        )
        
        has_non_us = any(
            keyword in location
            for keyword in Config.NON_US_LOCATION_KEYWORDS
        )
        
        # Exclude if non-US only (no US option)
        if has_non_us and not has_us:
            return False
        
        # 4. Check recency (Google Jobs provides jobPostedAt field)
        date_field = raw_data.get('jobPostedAt') or raw_data.get('jobPostedAtTimestamp')
        if date_field:
            try:
                # Handle timestamp (Unix timestamp in seconds)
                if isinstance(date_field, (int, float)):
                    posted_date = datetime.fromtimestamp(date_field)
                    age_days = (datetime.now() - posted_date).days
                    
                    if age_days > Config.MAX_JOB_AGE_DAYS:
                        return False
                
                # Handle string formats
                elif isinstance(date_field, str):
                    if 'T' in date_field:
                        posted_date = datetime.fromisoformat(date_field.replace('Z', '+00:00'))
                        now = datetime.now(posted_date.tzinfo) if posted_date.tzinfo else datetime.now()
                        age_days = (now - posted_date).days
                        
                        if age_days > Config.MAX_JOB_AGE_DAYS:
                            return False
                    elif 'ago' in date_field.lower():
                        # Parse "2 days ago", "1 week ago", etc.
                        parts = date_field.lower().split()
                        if len(parts) >= 2:
                            num = int(parts[0]) if parts[0].isdigit() else 1
                            unit = parts[1]
                            
                            if 'day' in unit:
                                age_days = num
                            elif 'week' in unit:
                                age_days = num * 7
                            elif 'month' in unit:
                                age_days = num * 30
                            else:
                                age_days = 0
                            
                            if age_days > Config.MAX_JOB_AGE_DAYS:
                                return False
            except Exception as e:
                pass  # If parsing fails, include the job
        
        return True
    
    def build_queries(self, job_titles: List[str], locations: List[str]) -> List[str]:
        """
        Build Google Jobs search queries from titles and locations.
        
        Args:
            job_titles: List of job titles
            locations: List of locations
        
        Returns:
            List of search query strings
        """
        queries = []
        
        for title in job_titles:
            for location in locations:
                query = f"{title} {location}"
                queries.append(query)
        
        return queries
