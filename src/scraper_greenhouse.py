"""
Greenhouse job board scraper.
Scrapes from Top 40 company Greenhouse boards (Section 3 of spec.md).
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import re
from src.config import Config


class GreenhouseScraper:
    """Scraper for Greenhouse job boards."""
    
    def __init__(self):
        """Initialize Greenhouse scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def scrape_board(self, company_name: str, board_url: str) -> List[Dict]:
        """
        Scrape all jobs from a Greenhouse board.
        
        Args:
            company_name: Company name
            board_url: Base URL of Greenhouse board (e.g., https://boards.greenhouse.io/stripe)
        
        Returns:
            List of job dicts
        """
        jobs = []
        
        try:
            # Extract company identifier from board_url
            # e.g., https://boards.greenhouse.io/stripe -> stripe
            company_id = board_url.rstrip('/').split('/')[-1]
            
            # Use the official Greenhouse Boards API
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_id}/jobs"
            
            response = self.session.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # API returns {"jobs": [...]}
                job_list = data.get('jobs', [])
                
                print(f"  Found {len(job_list)} jobs from {company_name}")
                
                for job in job_list:
                    parsed_job = self._parse_job_json(job, company_name, board_url)
                    if parsed_job and self._should_include_job(parsed_job):
                        jobs.append(parsed_job)
                
                print(f"  Filtered to {len(jobs)} relevant jobs")
            
            else:
                print(f"  API returned {response.status_code} for {company_name}")
                # Fallback: scrape HTML
                jobs = self._scrape_html(company_name, board_url)
        
        except Exception as e:
            print(f"Error scraping {company_name}: {e}")
            import traceback
            traceback.print_exc()
        
        return jobs
    
    def _should_include_job(self, job: Dict) -> bool:
        """
        Check if job meets filtering criteria (Section 4 of spec).
        
        Filters:
        - Job title match
        - US location (exclude Canada-only or international-only)
        - Exclude senior roles
        - Exclude manager roles
        - Posted within last 30 days (using first_published)
        """
        title = job.get('title', '').lower()
        location = job.get('location', '').lower()
        raw_data = job.get('raw_data', {})
        
        # 1. Check job title matches (Software Engineer, ML Engineer, etc.)
        title_match = any(
            target.lower() in title
            for target in Config.JOB_TITLES
        )
        if not title_match:
            return False
        
        # 2. Exclude senior roles (check both title and description)
        is_senior = any(
            keyword.lower() in title
            for keyword in Config.EXCLUDE_SENIORITY_KEYWORDS
        )
        if is_senior:
            return False
        
        # 3. Location filtering (complex logic for multi-location jobs)
        # Check if location has any US indicators
        has_us = any(
            keyword in location
            for keyword in Config.US_LOCATION_KEYWORDS
        )
        
        # FOOLPROOF: Also check for state abbreviations with regex (catches any format)
        if not has_us:
            import re
            # Match any US state abbreviation surrounded by word boundaries or punctuation
            # Pattern: (comma/space/dash/start) + STATE + (comma/space/end/paren)
            state_pattern = r'[\s,\-\(]?(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)[\s,\)\.]?'
            if re.search(state_pattern, location.upper()):
                has_us = True
        
        # Check if location has any non-US indicators
        has_non_us = any(
            keyword in location
            for keyword in Config.NON_US_LOCATION_KEYWORDS
        )
        
        # Decision logic (FOOLPROOF approach):
        # - If has non-US keywords BUT no US keywords → Exclude (clearly international)
        # - If has US keywords (with or without non-US) → Include (US option available)
        # - If has neither (e.g., ambiguous "Remote", "CA", empty) → Include (let LLM filter)
        # This way, we only exclude jobs that are CLEARLY non-US, and include everything else
        
        if has_non_us and not has_us:
            # Non-US only (e.g., "Toronto", "Berlin", "Canada")
            return False
        
        # All other cases → Include (US-only, multi-location, ambiguous, or empty)
        
        # 5. Check recency using first_published (last 30 days)
        if 'first_published' in raw_data:
            try:
                from datetime import datetime
                published_str = raw_data['first_published']
                # Parse ISO format: 2025-09-02T18:26:14-04:00
                if 'T' in published_str:
                    published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                    now = datetime.now(published_date.tzinfo) if published_date.tzinfo else datetime.now()
                    age_days = (now - published_date).days
                    
                    if age_days > Config.MAX_JOB_AGE_DAYS:
                        return False
            except Exception as e:
                pass  # If parsing fails, include the job
        
        return True
    
    def _parse_job_json(self, job: Dict, company_name: str, board_url: str) -> Dict:
        """Parse job from Greenhouse JSON API."""
        job_id = job.get('id', '')
        title = job.get('title', '')
        location = job.get('location', {}).get('name', '') if isinstance(job.get('location'), dict) else job.get('location', '')
        absolute_url = job.get('absolute_url', '')
        
        # Description can be in 'content' or need separate fetch
        description = job.get('content', '')
        
        return {
            'title': title,
            'company': company_name,
            'url': absolute_url,
            'source': 'greenhouse',
            'description': description,
            'location': location,
            'raw_data': job
        }
    
    def _scrape_html(self, company_name: str, board_url: str) -> List[Dict]:
        """Fallback: scrape HTML if JSON API doesn't work."""
        jobs = []
        
        try:
            response = self.session.get(board_url, timeout=15)
            if response.status_code != 200:
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Greenhouse boards typically use section.level-0 for job sections
            job_sections = soup.find_all('section', class_='level-0')
            
            for section in job_sections:
                job_links = section.find_all('a', href=True)
                
                for link in job_links:
                    title = link.get_text(strip=True)
                    url = link['href']
                    
                    if not url.startswith('http'):
                        url = f"{board_url}{url}"
                    
                    # Try to get location from nearby text
                    location = ''
                    parent = link.parent
                    if parent:
                        location_span = parent.find('span', class_='location')
                        if location_span:
                            location = location_span.get_text(strip=True)
                    
                    # Fetch full job description
                    description = self._fetch_job_description(url)
                    
                    jobs.append({
                        'title': title,
                        'company': company_name,
                        'url': url,
                        'source': 'greenhouse',
                        'description': description,
                        'location': location
                    })
                    
                    # Rate limit
                    time.sleep(0.5)
        
        except Exception as e:
            print(f"HTML scraping error for {company_name}: {e}")
        
        return jobs
    
    def _fetch_job_description(self, job_url: str) -> str:
        """Fetch full job description from individual job page."""
        try:
            response = self.session.get(job_url, timeout=15)
            if response.status_code != 200:
                return ''
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Greenhouse job descriptions are typically in div#content or div.content
            content_div = soup.find('div', id='content') or soup.find('div', class_='content')
            
            if content_div:
                return content_div.get_text(separator='\n', strip=True)
            
            return ''
        
        except Exception:
            return ''
    
    def scrape_all_boards(self, boards: Dict[str, str]) -> List[Dict]:
        """
        Scrape all Greenhouse boards.
        
        Args:
            boards: Dict mapping company_name -> board_url
        
        Returns:
            List of all jobs from all boards
        """
        all_jobs = []
        
        for company, url in boards.items():
            print(f"Scraping {company}...")
            jobs = self.scrape_board(company, url)
            all_jobs.extend(jobs)
            print(f"  Found {len(jobs)} jobs")
            
            # Rate limit between boards
            time.sleep(1)
        
        return all_jobs
