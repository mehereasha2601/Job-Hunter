"""
Main scraping orchestrator.
Coordinates all scrapers, runs H1B filter, deduplicates, and stores to database.
Section 9 of spec.md.
"""

import sys
from typing import List, Dict
from datetime import datetime

from src.config import Config
from src.db import Database
from src.h1b_filter import h1b_filter
from src.scraper_greenhouse import GreenhouseScraper
from src.scraper_jobspy import JobSpyScraper
from src.scraper_apify import ApifyScraper


class ScrapingOrchestrator:
    """Orchestrates all job scrapers and database storage."""
    
    def __init__(self):
        """Initialize orchestrator with all scrapers."""
        self.db = Database()
        self.greenhouse = GreenhouseScraper()
        self.jobspy = JobSpyScraper()
        
        if Config.APIFY_TOKEN:
            self.apify = ApifyScraper(Config.APIFY_TOKEN)
        else:
            self.apify = None
            print("Warning: APIFY_TOKEN not set, skipping Google Jobs scraper")
    
    def scrape_all(self) -> Dict:
        """
        Run all scrapers and store results.
        
        Returns:
            Summary dict with counts
        """
        print("=" * 60)
        print("STARTING JOB SCRAPING")
        print("=" * 60)
        
        all_jobs = []
        
        # Step 1: Greenhouse boards
        print("\n[1/3] Scraping Greenhouse boards...")
        greenhouse_jobs = self.greenhouse.scrape_all_boards(Config.GREENHOUSE_BOARDS)
        print(f"✓ Found {len(greenhouse_jobs)} jobs from Greenhouse")
        all_jobs.extend(greenhouse_jobs)
        
        # Step 2: JobSpy (LinkedIn, Indeed, ZipRecruiter)
        print("\n[2/3] Scraping via JobSpy...")
        jobspy_jobs = self.jobspy.scrape_multiple_queries(
            job_titles=Config.JOB_TITLES,
            locations=Config.LOCATIONS,
            results_per_query=50
        )
        # Normalize JobSpy output
        normalized_jobspy = [self.jobspy.normalize_job(job) for job in jobspy_jobs]
        print(f"✓ Found {len(normalized_jobspy)} jobs from JobSpy")
        all_jobs.extend(normalized_jobspy)
        
        # Step 3: Apify Google Jobs
        if self.apify:
            print("\n[3/3] Scraping via Apify Google Jobs...")
            queries = self.apify.build_queries(Config.JOB_TITLES, Config.LOCATIONS)
            apify_jobs = self.apify.run_scraper(queries, max_results_per_query=100)
            normalized_apify = [self.apify.normalize_job(job) for job in apify_jobs]
            print(f"✓ Found {len(normalized_apify)} jobs from Apify")
            all_jobs.extend(normalized_apify)
        else:
            print("\n[3/3] Skipping Apify (no API token)")
        
        print(f"\nTotal jobs scraped: {len(all_jobs)}")
        
        # Step 4: H1B filter and dedup
        print("\n[4/5] Running H1B filter...")
        filtered_jobs = self._filter_jobs(all_jobs)
        print(f"✓ {len(filtered_jobs)} jobs passed H1B filter")
        
        # Step 5: Store to database
        print("\n[5/5] Storing to database...")
        stats = self._store_jobs(filtered_jobs)
        
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Total scraped: {len(all_jobs)}")
        print(f"After H1B filter: {len(filtered_jobs)}")
        print(f"New jobs inserted: {stats['new']}")
        print(f"Duplicates skipped: {stats['duplicates']}")
        print(f"Errors: {stats['errors']}")
        
        return {
            'total_scraped': len(all_jobs),
            'after_filter': len(filtered_jobs),
            'new': stats['new'],
            'duplicates': stats['duplicates'],
            'errors': stats['errors']
        }
    
    def _filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Apply H1B filter to jobs."""
        filtered = []
        
        for job in jobs:
            if not h1b_filter:
                # No filter loaded, keep all jobs
                filtered.append(job)
                continue
            
            # Run H1B classification
            h1b_result = h1b_filter.classify_job(
                company=job.get('company', ''),
                description=job.get('description', '')
            )
            
            # Skip blocked jobs
            if h1b_result['h1b_flag'] == 'blocked':
                continue
            
            # Annotate job with H1B info
            job['h1b_flag'] = h1b_result['h1b_flag']
            job['on_target_list'] = h1b_result['on_target_list']
            
            filtered.append(job)
        
        return filtered
    
    def _store_jobs(self, jobs: List[Dict]) -> Dict:
        """
        Store jobs to database with deduplication.
        
        Returns:
            Stats dict
        """
        new_count = 0
        duplicate_count = 0
        error_count = 0
        
        for job in jobs:
            try:
                # Check if job exists
                job_id = self.db.generate_job_id(
                    job.get('url', ''),
                    job.get('company', ''),
                    job.get('title', '')
                )
                
                existing = self.db.get_job(job_id)
                
                if existing:
                    duplicate_count += 1
                else:
                    self.db.insert_job(job)
                    new_count += 1
            
            except Exception as e:
                print(f"Error storing job: {e}")
                error_count += 1
        
        return {
            'new': new_count,
            'duplicates': duplicate_count,
            'errors': error_count
        }


def main():
    """Main entry point for scraper."""
    try:
        orchestrator = ScrapingOrchestrator()
        results = orchestrator.scrape_all()
        
        print("\nScraping session complete!")
        return 0
    
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
