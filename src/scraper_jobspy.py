"""
JobSpy wrapper for LinkedIn, Indeed, and ZipRecruiter scraping.
Section 10 of spec.md.
"""

import time
from typing import List, Dict
from datetime import datetime, timedelta
# Commented out for Phase 1 - uncomment when ready for Phase 2
# from python_jobspy import scrape_jobs

from .config import Config


class JobSpyScraper:
    """Wrapper for python-jobspy to scrape LinkedIn, Indeed, ZipRecruiter."""
    
    def __init__(self):
        """Initialize JobSpy scraper."""
        pass
    
    def scrape_jobs(
        self,
        search_term: str,
        location: str = '',
        results_wanted: int = 50,
        site_name: List[str] = ['linkedin', 'indeed', 'zip_recruiter']
    ) -> List[Dict]:
        """
        Scrape jobs using JobSpy.
        
        Args:
            search_term: Job title or keywords
            location: Location string
            results_wanted: Max results per site
            site_name: List of sites to scrape
        
        Returns:
            List of filtered job dicts
        """
        jobs = []
        
        try:
            # Uncomment when python-jobspy is installed
            # df = scrape_jobs(
            #     site_name=site_name,
            #     search_term=search_term,
            #     location=location,
            #     results_wanted=results_wanted,
            #     hours_old=72,
            #     country_indeed='USA',
            #     linkedin_fetch_description=True
            # )
            # 
            # if df is not None and not df.empty:
            #     raw_jobs = df.to_dict('records')
            #     
            #     # Normalize and filter jobs
            #     for raw_job in raw_jobs:
            #         normalized = self.normalize_job(raw_job)
            #         
            #         # Apply filtering logic
            #         if self._should_include_job(normalized):
            #             jobs.append(normalized)
            #     
            #     print(f"  JobSpy: Found {len(raw_jobs)} jobs, filtered to {len(jobs)}")
            
            print(f"JobSpy: Would scrape {search_term} in {location} from {site_name}")
            print("(python-jobspy currently disabled for Phase 1)")
        
        except Exception as e:
            print(f"JobSpy error: {e}")
        
        return jobs
    
    def scrape_multiple_queries(
        self,
        job_titles: List[str],
        locations: List[str],
        results_per_query: int = 50
    ) -> List[Dict]:
        """
        Scrape multiple combinations of job titles and locations.
        
        Args:
            job_titles: List of job titles to search
            locations: List of locations to search
            results_per_query: Max results per query
        
        Returns:
            Combined list of jobs from all queries
        """
        all_jobs = []
        
        for title in job_titles:
            for location in locations:
                print(f"Searching: {title} in {location}")
                jobs = self.scrape_jobs(
                    search_term=title,
                    location=location,
                    results_wanted=results_per_query
                )
                all_jobs.extend(jobs)
                
                # Rate limit between queries
                time.sleep(2)
        
        return all_jobs
    
    def normalize_job(self, job: Dict) -> Dict:
        """
        Normalize JobSpy output to standard format.
        
        Args:
            job: Raw job dict from JobSpy
        
        Returns:
            Normalized job dict matching our schema
        """
        source_mapping = {
            'linkedin': 'linkedin',
            'indeed': 'indeed',
            'zip_recruiter': 'ziprecruiter'
        }
        
        return {
            'title': job.get('title', ''),
            'company': job.get('company', ''),
            'url': job.get('job_url', ''),
            'source': source_mapping.get(job.get('site', ''), 'jobspy'),
            'description': job.get('description', ''),
            'location': job.get('location', ''),
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
        raw_data = job.get('raw_data', job)  # Use job itself if no raw_data
        
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
        
        # 4. Check recency (JobSpy provides date_posted field)
        date_field = raw_data.get('date_posted') or raw_data.get('posted_at')
        if date_field:
            try:
                # JobSpy uses various date formats
                if isinstance(date_field, str):
                    if 'T' in date_field:
                        # ISO format
                        posted_date = datetime.fromisoformat(date_field.replace('Z', '+00:00'))
                    else:
                        # Try common formats
                        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
                            try:
                                posted_date = datetime.strptime(date_field, fmt)
                                break
                            except:
                                continue
                        else:
                            return True  # Can't parse, include it
                    
                    now = datetime.now(posted_date.tzinfo) if posted_date.tzinfo else datetime.now()
                    age_days = (now - posted_date).days
                    
                    if age_days > Config.MAX_JOB_AGE_DAYS:
                        return False
            except Exception as e:
                pass  # If parsing fails, include the job
        
        return True
