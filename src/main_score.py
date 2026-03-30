"""
Step 1: Score unscored jobs and send digest email.
Sections 5 and 9 of spec.md.
"""

import sys
from typing import List, Dict
from datetime import datetime

from src.config import Config
from src.db import Database
from src.scorer import JobScorer
from src.notifier import send_digest_email


def load_resume() -> str:
    """Load master resume from file."""
    with open('resume.txt', 'r', encoding='utf-8') as f:
        return f.read()


def main():
    """Main entry point for Step 1."""
    print("=" * 60)
    print("STEP 1: JOB SCORING & DIGEST")
    print("=" * 60)
    
    try:
        # Load resume
        print("\n[1/5] Loading master resume...")
        resume_text = load_resume()
        print(f"✓ Loaded resume ({len(resume_text)} chars)")
        
        # Initialize components
        print("\n[2/5] Initializing database and scorer...")
        db = Database()
        scorer = JobScorer(resume_text)
        print("✓ Components ready")
        
        # Get unscored jobs
        print("\n[3/5] Fetching unscored jobs...")
        unscored_jobs = db.get_unscored_jobs()
        print(f"✓ Found {len(unscored_jobs)} unscored jobs")
        
        if len(unscored_jobs) == 0:
            print("\nNo jobs to score. Exiting.")
            return 0
        
        # Score each job
        print(f"\n[4/5] Scoring {len(unscored_jobs)} jobs...")
        scored_jobs = []
        
        for i, job in enumerate(unscored_jobs, 1):
            print(f"\n  [{i}/{len(unscored_jobs)}] {job['title']} at {job['company']}")

            if Config.title_is_non_fulltime(job.get('title', '')):
                print("    Skipped (non-full-time title); score set to 0")
                db.update_job_score(
                    job_id=job['id'],
                    score=0.0,
                    h1b_flag=job.get('h1b_flag', 'unknown'),
                )
                continue

            score, reasoning = scorer.score_job(job)
            
            # Extract tech stack
            tech_stack = scorer.extract_tech_stack(job.get('description', ''))
            
            print(f"    Score: {score:.1f}/10")
            print(f"    Tech: {', '.join(tech_stack[:5])}")
            
            # Update database
            db.update_job_score(
                job_id=job['id'],
                score=score,
                h1b_flag=job.get('h1b_flag', 'unknown')
            )
            
            # Add to scored jobs for digest
            job['score'] = score
            job['reasoning'] = reasoning
            job['tech_stack'] = tech_stack
            scored_jobs.append(job)
        
        print(f"\n✓ Scored all {len(scored_jobs)} jobs")
        
        # Filter for high-scoring jobs
        high_scoring = [j for j in scored_jobs if j['score'] >= 7.0]
        print(f"✓ {len(high_scoring)} jobs scored 7.0+")
        
        # Step 5: Send digest email
        print("\n[5/5] Sending digest email...")
        
        if len(high_scoring) > 0:
            if Config.NOTIFICATION_EMAIL and Config.GMAIL_APP_PASSWORD:
                email_result = send_digest_email(high_scoring)
                if email_result['success']:
                    print(f"✓ Digest email sent to {Config.NOTIFICATION_EMAIL}")
                else:
                    print(f"✗ Email failed: {email_result['error']}")
            else:
                print("⚠ Email not configured (NOTIFICATION_EMAIL or GMAIL_APP_PASSWORD missing)")
                print("  (Skipping email, but scores are saved to database)")
        else:
            print("⚠ No high-scoring jobs (7.0+), skipping email")
        
        print("\n" + "=" * 60)
        print("STEP 1 COMPLETE")
        print("=" * 60)
        print(f"Jobs scored: {len(scored_jobs)}")
        print(f"High-scoring (7.0+): {len(high_scoring)}")
        print(f"Email sent: {'Yes' if (len(high_scoring) > 0 and Config.NOTIFICATION_EMAIL) else 'No'}")
        
        return 0
    
    except Exception as e:
        print(f"Fatal error in Step 1: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
