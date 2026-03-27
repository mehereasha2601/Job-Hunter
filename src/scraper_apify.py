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
        # Extract date_posted from jobPostedAt field and normalize to ISO format
        date_posted = None
        if 'jobPostedAt' in job:
            date_str = job['jobPostedAt']
            if date_str:
                try:
                    from datetime import datetime, timedelta
                    # Parse relative time strings like "5 hours ago", "2 days ago"
                    if 'ago' in date_str.lower():
                        parts = date_str.lower().split()
                        if len(parts) >= 2:
                            num = int(parts[0])
                            unit = parts[1]
                            
                            if 'hour' in unit:
                                date_posted = (datetime.now() - timedelta(hours=num)).isoformat()
                            elif 'day' in unit:
                                date_posted = (datetime.now() - timedelta(days=num)).isoformat()
                            elif 'week' in unit:
                                date_posted = (datetime.now() - timedelta(weeks=num)).isoformat()
                    elif 'T' in date_str:
                        # Already ISO format
                        date_posted = date_str
                except:
                    date_posted = date_str  # Store as-is if parsing fails
        
        elif 'jobPostedAtTimestamp' in job:
            # Convert Unix timestamp to ISO format
            try:
                from datetime import datetime
                timestamp = job['jobPostedAtTimestamp']
                if isinstance(timestamp, (int, float)):
                    date_posted = datetime.fromtimestamp(timestamp).isoformat()
            except:
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
        
        # 3. Location filtering (FOOLPROOF approach)
        has_us = any(
            keyword in location
            for keyword in Config.US_LOCATION_KEYWORDS
        )
        
        # FOOLPROOF: Also check for state abbreviations with regex (catches any format)
        if not has_us:
            import re
            # Match any US state abbreviation surrounded by word boundaries or punctuation
            state_pattern = r'[\s,\-\(]?(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)[\s,\)\.]?'
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
