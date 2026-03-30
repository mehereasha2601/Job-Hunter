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
        self.actor_id = 'johnvc/google-jobs-scraper'  # Most popular Google Jobs scraper
    
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
        from src.job_date_utils import parse_iso_datetime, parse_relative_posted_at

        # Extract date_posted from jobPostedAt / timestamp (strict normalization for DB display)
        date_posted = None
        if job.get("jobPostedAt"):
            date_str = job["jobPostedAt"]
            if isinstance(date_str, str) and date_str.strip():
                try:
                    if "ago" in date_str.lower():
                        dt = parse_relative_posted_at(date_str)
                    else:
                        dt = parse_iso_datetime(date_str)
                    if dt:
                        date_posted = dt.isoformat()
                except Exception:
                    pass
        elif job.get("jobPostedAtTimestamp") is not None:
            try:
                timestamp = job["jobPostedAtTimestamp"]
                if isinstance(timestamp, (int, float)):
                    date_posted = datetime.fromtimestamp(timestamp).isoformat()
            except Exception:
                pass
        
        return {
            'title': job.get('jobTitle', ''),
            'company': job.get('employerName', ''),
            'url': job.get('jobApplyLink', ''),
            'source': f"google ({job.get('jobPublisher', 'unknown')})",
            'description': job.get('jobDescription', ''),
            'location': job.get('jobLocation', ''),
            'date_posted': date_posted,  # Normalized to ISO format
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
        - Posted within last MAX_JOB_AGE_DAYS (verifiable date required)
        """
        title = job.get('title', '').lower()
        location = job.get('location', '').lower()
        raw_data = job.get('raw_data', job)

        if Config.title_is_non_fulltime(job.get('title', '')):
            return False

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
        
        # 3. Location filtering (FOOLPROOF approach)
        has_us = any(
            keyword in location
            for keyword in Config.US_LOCATION_KEYWORDS
        )
        
        # FOOLPROOF: Also check for state abbreviations with regex (catches any format)
        if not has_us:
            import re
            # Use strict word boundaries so we don't match state codes inside words
            # (e.g. "INDIA" should not match "IN", "LONDON" should not match "ND")
            state_pattern = r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b'
            if re.search(state_pattern, location.upper()):
                has_us = True
        
        has_non_us = any(
            keyword in location
            for keyword in Config.NON_US_LOCATION_KEYWORDS
        )
        
        # ONLY exclude if clearly non-US (has non-US keywords but no US keywords)
        # Include everything else: US-only, multi-location, ambiguous, or empty
        if has_non_us and not has_us:
            return False
        
        # 4. Recency — require verifiable posted time (actor also uses datePosted=today upstream)
        from src.job_date_utils import age_days_since_posted, parse_iso_datetime, parse_relative_posted_at

        date_field = raw_data.get("jobPostedAt") or raw_data.get("jobPostedAtTimestamp")
        if date_field is None:
            return False

        posted_date = None
        try:
            if isinstance(date_field, (int, float)):
                posted_date = datetime.fromtimestamp(date_field)
            elif isinstance(date_field, str):
                if "ago" in date_field.lower():
                    posted_date = parse_relative_posted_at(date_field)
                else:
                    posted_date = parse_iso_datetime(date_field)
        except Exception:
            return False

        if posted_date is None:
            return False
        if age_days_since_posted(posted_date) > Config.MAX_JOB_AGE_DAYS:
            return False

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
