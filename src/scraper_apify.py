"""
Apify Google Jobs scraper wrapper.
Uses Apify's Google Jobs Scraper actor (Section 11 of spec.md).
"""

import requests
from typing import List, Dict
import time
from datetime import datetime

from .config import Config


class ApifyScraper:
    """Wrapper for Apify Google Jobs Scraper."""
    
    def __init__(self, api_token: str):
        """
        Initialize Apify scraper.
        
        Args:
            api_token: Apify API token
        """
        self.api_token = api_token
        self.actor_id = 'misceres/google-jobs-scraper'
        self.base_url = 'https://api.apify.com/v2'
    
    def run_scraper(
        self,
        queries: List[str],
        max_results_per_query: int = 100
    ) -> List[Dict]:
        """
        Run Google Jobs scraper actor.
        
        Args:
            queries: List of search queries
            max_results_per_query: Max results per query
        
        Returns:
            List of job dicts
        """
        jobs = []
        
        try:
            # Build actor input
            actor_input = {
                'queries': queries,
                'maxConcurrency': 5,
                'maxPagesPerQuery': max_results_per_query // 10,
                'languageCode': 'en',
                'countryCode': 'us'
            }
            
            # Start actor run
            run_url = f"{self.base_url}/acts/{self.actor_id}/runs?token={self.api_token}"
            
            print(f"Starting Apify actor for {len(queries)} queries...")
            response = requests.post(run_url, json=actor_input, timeout=30)
            
            if response.status_code not in [200, 201]:
                print(f"Error starting actor: {response.status_code}")
                return jobs
            
            run_data = response.json()['data']
            run_id = run_data['id']
            
            # Poll for completion
            jobs = self._wait_for_results(run_id)
        
        except Exception as e:
            print(f"Apify scraper error: {e}")
        
        return jobs
    
    def _wait_for_results(self, run_id: str, max_wait: int = 600) -> List[Dict]:
        """
        Wait for actor run to complete and fetch results.
        
        Args:
            run_id: Actor run ID
            max_wait: Max seconds to wait
        
        Returns:
            List of jobs
        """
        start_time = time.time()
        check_url = f"{self.base_url}/actor-runs/{run_id}?token={self.api_token}"
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(check_url, timeout=30)
                if response.status_code != 200:
                    time.sleep(5)
                    continue
                
                run_data = response.json()['data']
                status = run_data['status']
                
                if status == 'SUCCEEDED':
                    print(f"Actor run completed in {int(time.time() - start_time)}s")
                    return self._fetch_dataset(run_data['defaultDatasetId'])
                
                elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                    print(f"Actor run {status}")
                    return []
                
                else:
                    # Still running
                    print(f"Actor running... ({status})")
                    time.sleep(10)
            
            except Exception as e:
                print(f"Error checking run status: {e}")
                time.sleep(5)
        
        print(f"Actor run timeout after {max_wait}s")
        return []
    
    def _fetch_dataset(self, dataset_id: str) -> List[Dict]:
        """Fetch results from dataset and apply filtering."""
        try:
            dataset_url = f"{self.base_url}/datasets/{dataset_id}/items?token={self.api_token}"
            response = requests.get(dataset_url, timeout=30)
            
            if response.status_code != 200:
                return []
            
            items = response.json()
            
            # Normalize and filter jobs
            normalized = []
            for item in items:
                job = self.normalize_job(item)
                
                # Apply filtering logic
                if self._should_include_job(job):
                    normalized.append(job)
            
            print(f"  Apify: Found {len(items)} jobs, filtered to {len(normalized)}")
            return normalized
        
        except Exception as e:
            print(f"Error fetching dataset: {e}")
            return []
    
    def normalize_job(self, job: Dict) -> Dict:
        """
        Normalize Apify output to standard format.
        
        Args:
            job: Raw job dict from Apify
        
        Returns:
            Normalized job dict
        """
        return {
            'title': job.get('title', ''),
            'company': job.get('companyName', ''),
            'url': job.get('jobUrl', ''),
            'source': 'google',
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
        
        # 4. Check recency (Google Jobs provides publishedDate)
        date_field = raw_data.get('publishedDate') or raw_data.get('datePosted')
        if date_field:
            try:
                # Google Jobs uses ISO format or various date strings
                if isinstance(date_field, str):
                    if 'T' in date_field:
                        posted_date = datetime.fromisoformat(date_field.replace('Z', '+00:00'))
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
                    else:
                        # Try parsing standard date formats
                        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
                            try:
                                posted_date = datetime.strptime(date_field, fmt)
                                age_days = (datetime.now() - posted_date).days
                                
                                if age_days > Config.MAX_JOB_AGE_DAYS:
                                    return False
                                break
                            except:
                                continue
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
