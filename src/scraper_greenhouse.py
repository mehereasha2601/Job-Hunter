"""
Greenhouse job board scraper.
Scrapes from Top 40 company Greenhouse boards (Section 3 of spec.md).
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import re


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
            board_url: Base URL of Greenhouse board
        
        Returns:
            List of job dicts
        """
        jobs = []
        
        try:
            # Try JSON API endpoint first (most Greenhouse boards have this)
            api_url = f"{board_url}/jobs"
            params = {'content': 'true'}
            
            response = self.session.get(api_url, params=params, timeout=15)
            
            if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
                # Parse JSON response
                data = response.json()
                
                if isinstance(data, dict) and 'jobs' in data:
                    job_list = data['jobs']
                elif isinstance(data, list):
                    job_list = data
                else:
                    job_list = []
                
                for job in job_list:
                    jobs.append(self._parse_job_json(job, company_name, board_url))
            
            else:
                # Fallback: scrape HTML
                jobs = self._scrape_html(company_name, board_url)
        
        except Exception as e:
            print(f"Error scraping {company_name}: {e}")
        
        return jobs
    
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
