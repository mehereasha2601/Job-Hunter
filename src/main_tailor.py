"""
Step 2: Generate tailored resumes and cold emails for selected jobs.
Section 14 of spec.md.
"""

import sys
from typing import List, Dict
from datetime import datetime
import os

from src.config import Config
from src.db import Database
from src.resume_tailor import ResumeTailor
from src.email_drafter import EmailDrafter
from src.cover_letter import CoverLetterGenerator
from src.guardrails import Guardrails
from src.google_docs import GoogleDocsClient
from src.output import save_markdown_backup
from src.notifier import send_tailor_complete_email


def load_resume() -> str:
    """Load master resume from file."""
    with open('resume.txt', 'r', encoding='utf-8') as f:
        return f.read()


def main(job_ids: List[str]):
    """
    Main entry point for Step 2.
    
    Args:
        job_ids: List of job IDs to tailor for
    """
    print("=" * 60)
    print("STEP 2: TAILORING & OUTPUT GENERATION")
    print("=" * 60)
    
    try:
        # Initialize components
        print("\n[1/7] Loading master resume...")
        resume_text = load_resume()
        print(f"✓ Loaded resume ({len(resume_text)} chars)")
        
        print("\n[2/7] Initializing components...")
        db = Database()
        tailor = ResumeTailor(resume_text)
        drafter = EmailDrafter(resume_text)
        cover_letter_gen = CoverLetterGenerator(resume_text)
        guardrails = Guardrails(resume_text)
        
        # Initialize Google Docs if credentials available
        google_docs = None
        if Config.GOOGLE_CREDENTIALS_JSON:
            google_docs = GoogleDocsClient()
            print("✓ Components ready (including Google Docs)")
        else:
            print("⚠ Google Docs not configured, will skip doc creation")
        
        # Get jobs to tailor
        print(f"\n[3/7] Fetching {len(job_ids)} jobs...")
        jobs = db.get_jobs_to_tailor(job_ids)
        print(f"✓ Loaded {len(jobs)} jobs")
        
        if len(jobs) == 0:
            print("\nNo jobs found. Exiting.")
            return 0
        
        # Process each job
        print(f"\n[4/7] Generating tailored content for {len(jobs)} jobs...")
        results = []
        
        for i, job in enumerate(jobs, 1):
            print(f"\n  [{i}/{len(jobs)}] {job['title']} at {job['company']}")
            result = _process_job(job, tailor, drafter, cover_letter_gen, guardrails, google_docs, db)
            results.append(result)
        
        # Count successes
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n✓ Completed {len(successful)}/{len(jobs)} jobs")
        if len(failed) > 0:
            print(f"⚠ {len(failed)} jobs failed")
        
        # Send completion email
        print("\n[7/7] Sending completion email...")
        if len(successful) > 0:
            email_result = send_tailor_complete_email(successful)
            if email_result['success']:
                print(f"✓ Email sent to {Config.NOTIFICATION_EMAIL}")
            else:
                print(f"✗ Email failed: {email_result['error']}")
        else:
            print("⚠ No successful jobs, skipping email")
        
        print("\n" + "=" * 60)
        print("STEP 2 COMPLETE")
        print("=" * 60)
        print(f"Jobs processed: {len(jobs)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        return 0
    
    except Exception as e:
        print(f"Fatal error in Step 2: {e}")
        return 1


def _process_job(
    job: Dict,
    tailor: ResumeTailor,
    drafter: EmailDrafter,
    cover_letter_gen: CoverLetterGenerator,
    guardrails: Guardrails,
    google_docs: GoogleDocsClient,
    db: Database
) -> Dict:
    """
    Process a single job: tailor resume, draft emails, run guardrails, create docs.
    
    Returns:
        Result dict with success status and all output URLs
    """
    job_id = job['id']
    title = job['title']
    company = job['company']
    
    try:
        # Step 1: Tailor resume
        print("    [1/6] Tailoring resume...")
        resume_result = tailor.tailor_resume(
            job_description=job['description'],
            company=job['company'],
            role=job['title']
        )
        
        if not resume_result['success']:
            error = f"Resume generation failed: {resume_result.get('error', 'Unknown')}"
            db.mark_job_error(job_id, error)
            return {'success': False, 'error': error, 'job': job}
        
        tailored_resume = resume_result['resume']
        print(f"    ✓ Resume generated ({len(tailored_resume)} chars)")
        
        # Step 2: Draft cold emails
        print("    [2/6] Drafting cold emails...")
        email_result = drafter.draft_emails(
            job_description=job['description'],
            company=job['company'],
            role=job['title']
        )
        
        if not email_result['success']:
            error = f"Email generation failed: {email_result.get('error', 'Unknown')}"
            db.mark_job_error(job_id, error)
            return {'success': False, 'error': error, 'job': job}
        
        emails = email_result['emails']
        print(f"    ✓ Emails generated")
        
        # Step 2.5: Generate cover letter (if required)
        cover_letter = None
        if cover_letter_gen.check_if_required(job['description']):
            print("    [2.5/6] Generating cover letter (required by JD)...")
            cover_result = cover_letter_gen.generate(
                job_description=job['description'],
                company=job['company'],
                role=job['title']
            )
            
            if cover_result['success']:
                cover_letter = cover_result['cover_letter']
                print(f"    ✓ Cover letter generated")
            else:
                print(f"    ⚠ Cover letter failed: {cover_result['error']}")
        
        # Step 3: Run guardrails
        print("    [3/6] Running guardrails...")
        
        # Resume guardrails
        g1_resume = guardrails.check_hallucination(tailored_resume)
        g2_resume = guardrails.check_banned_phrases(tailored_resume)
        g3_resume = guardrails.score_keyword_match(tailored_resume, job['description'])
        g4_resume = guardrails.check_length(tailored_resume)
        
        # Email guardrails (check both versions)
        email_text = emails['hiring_manager']['body'] + '\n' + emails['recruiter']['body']
        g2_email = guardrails.check_banned_phrases(email_text)
        
        # Check if passed
        all_passed = (
            g1_resume['passed'] and
            g2_resume['passed'] and
            g3_resume['passed'] and
            g4_resume['passed'] and
            g2_email['passed']
        )
        
        if not all_passed:
            flags = []
            if not g1_resume['passed']:
                flags.append(f"Hallucination: {g1_resume['flags']}")
            if not g2_resume['passed']:
                flags.append(f"Banned phrases (resume): {g2_resume['flags']}")
            if not g2_email['passed']:
                flags.append(f"Banned phrases (email): {g2_email['flags']}")
            if not g3_resume['passed']:
                flags.append(f"Low keyword match: {g3_resume['score']:.1f}%")
            if not g4_resume['passed']:
                flags.append(f"Length violation: {g4_resume['char_count']} chars")
            
            error = f"Guardrail failures: {'; '.join(flags)}"
            print(f"    ✗ Guardrails failed")
            db.mark_job_error(job_id, error)
            return {'success': False, 'error': error, 'job': job}
        
        print(f"    ✓ All guardrails passed (keyword match: {g3_resume['score']:.1f}%)")
        
        # Step 4: Save markdown backup
        print("    [4/6] Saving markdown backup...")
        md_path = save_markdown_backup(job, tailored_resume, emails, cover_letter)
        print(f"    ✓ Saved to {md_path}")
        
        # Step 5: Create Google Docs
        resume_pdf_url = ''
        doc_url = ''
        email_doc_url = ''
        
        if google_docs:
            print("    [5/6] Creating Google Docs...")
            
            # Resume doc
            doc_title = f"Resume — {company} — {title} — {datetime.now().strftime('%Y-%m-%d')}"
            doc_url = google_docs.create_resume_doc(doc_title, tailored_resume)
            print(f"    ✓ Resume doc created")
            
            # Email doc
            email_title = f"Cold Emails — {company} — {title} — {datetime.now().strftime('%Y-%m-%d')}"
            email_doc_url = google_docs.create_email_doc(email_title, emails)
            print(f"    ✓ Email doc created")
            
            # TODO: PDF generation from LaTeX (Phase 2.5)
            resume_pdf_url = ''
        else:
            print("    [5/6] Skipping Google Docs (not configured)")
        
        # Step 6: Update database
        print("    [6/6] Updating database...")
        db.update_job_tailored(
            job_id=job_id,
            resume_pdf_url=resume_pdf_url,
            doc_url=doc_url,
            email_doc_url=email_doc_url,
            md_path=md_path
        )
        print(f"    ✓ Database updated")
        
        return {
            'success': True,
            'job': job,
            'title': title,
            'company': company,
            'resume_pdf_url': resume_pdf_url,
            'doc_url': doc_url,
            'email_doc_url': email_doc_url,
            'md_path': md_path
        }
    
    except Exception as e:
        error = f"Error processing job: {str(e)}"
        print(f"    ✗ {error}")
        db.mark_job_error(job_id, error)
        return {'success': False, 'error': error, 'job': job}


if __name__ == '__main__':
    # Example: python src/main_tailor.py job_id1 job_id2 job_id3
    if len(sys.argv) < 2:
        print("Usage: python src/main_tailor.py <job_id1> [job_id2] ...")
        sys.exit(1)
    
    job_ids = sys.argv[1:]
    sys.exit(main(job_ids))
