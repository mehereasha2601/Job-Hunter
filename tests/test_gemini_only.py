"""
Gemini-only test harness.
Use this when Groq is rate limited to still test with Gemini.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import LLMClient
from src.resume_tailor import ResumeTailor
from src.email_drafter import EmailDrafter
from src.guardrails import Guardrails


def load_test_jobs(test_jobs_path: str):
    """Load test job listings from JSON file."""
    with open(test_jobs_path, 'r') as f:
        return json.load(f)


def load_master_resume(resume_path: str):
    """Load master resume from text file."""
    with open(resume_path, 'r') as f:
        return f.read()


def run_test_for_job(job: dict, master_resume: str, output_dir: Path):
    """Run test for a single job with Gemini."""
    print(f"\n{'='*80}")
    print(f"Testing: {job['company']} - {job['role']}")
    print(f"Provider: GEMINI")
    print(f"{'='*80}")
    
    results = {
        'job': job,
        'provider': 'gemini',
        'timestamp': datetime.now().isoformat()
    }
    
    # Initialize components
    resume_tailor = ResumeTailor(master_resume)
    email_drafter = EmailDrafter(master_resume)
    guardrails = Guardrails(master_resume)
    
    # Step 1: Generate tailored resume
    print(f"[gemini] Generating tailored resume...")
    resume_result = resume_tailor.tailor_resume(
        job_description=job['description'],
        company=job['company'],
        role=job['role'],
        provider='gemini'
    )
    results['resume'] = resume_result
    
    if not resume_result['success']:
        print(f"[gemini] Resume generation FAILED: {resume_result['error']}")
        return results
    
    print(f"[gemini] Resume generated successfully ({len(resume_result['resume_text'])} chars)")
    
    # Step 2: Generate cold emails
    print(f"[gemini] Generating cold emails...")
    email_result = email_drafter.draft_emails(
        job_description=job['description'],
        company=job['company'],
        role=job['role'],
        provider='gemini'
    )
    results['emails'] = email_result
    
    if not email_result['success']:
        print(f"[gemini] Email generation FAILED: {email_result['error']}")
        return results
    
    print(f"[gemini] Emails generated successfully")
    
    # Step 3: Run all guardrails
    print(f"[gemini] Running guardrails...")
    guardrail_results = guardrails.run_all(
        resume_text=resume_result['resume_text'],
        email_hiring_manager=email_result['hiring_manager'],
        email_recruiter=email_result['recruiter'],
        job_description=job['description']
    )
    results['guardrails'] = guardrail_results
    
    # Print guardrail summary
    print(f"\n[gemini] Guardrail Results:")
    print(f"  1. Hallucination: {'✓ PASSED' if guardrail_results['hallucination']['passed'] else '✗ FAILED'}")
    if not guardrail_results['hallucination']['passed']:
        for flag in guardrail_results['hallucination']['flags']:
            print(f"     - {flag}")
    
    print(f"  2. Banned Phrases: {'✓ PASSED' if guardrail_results['banned_phrases']['passed'] else '✗ FAILED'}")
    if not guardrail_results['banned_phrases']['passed']:
        for phrase in guardrail_results['banned_phrases']['found']:
            print(f"     - Found: '{phrase}'")
    
    print(f"  3. Keyword Match: {guardrail_results['keyword_match']['score']}% ({guardrail_results['keyword_match']['matched']}/{guardrail_results['keyword_match']['total']} keywords)")
    
    print(f"  4. Length: {'✓ PASSED' if guardrail_results['length']['passed'] else '✗ FAILED'} ({guardrail_results['length']['char_count']}/{guardrail_results['length']['max_chars']} chars, {guardrail_results['length']['percentage']}%)")
    
    print(f"\n[gemini] Overall: {'✓ ALL PASSED' if guardrail_results['passed'] else '✗ FAILED'}")
    
    # Save results
    job_safe_name = f"{job['company'].replace(' ', '_')}_{job['role'].replace(' ', '_').replace('/', '_')}"
    
    output_file = output_dir / f"{job_safe_name}_gemini.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    resume_file = output_dir / f"{job_safe_name}_gemini_resume.txt"
    with open(resume_file, 'w') as f:
        f.write(resume_result['resume_text'])
    
    email_file = output_dir / f"{job_safe_name}_gemini_emails.txt"
    with open(email_file, 'w') as f:
        f.write("=== HIRING MANAGER VERSION ===\n")
        f.write(f"Subject: {email_result['hiring_manager']['subject']}\n\n")
        f.write(f"{email_result['hiring_manager']['body']}\n\n")
        f.write("=== RECRUITER VERSION ===\n")
        f.write(f"Subject: {email_result['recruiter']['subject']}\n\n")
        f.write(f"{email_result['recruiter']['body']}\n")
    
    return results


def main():
    """Run Gemini-only test harness."""
    print("="*80)
    print("Gemini-Only Test Harness — Resume & Email Generation")
    print("="*80)
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    test_jobs_path = project_root / "tests" / "test_jobs.json"
    resume_path = project_root / "resume.txt"
    output_dir = project_root / "test_output_gemini"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Load data
    print(f"\nLoading test jobs from: {test_jobs_path}")
    test_jobs = load_test_jobs(str(test_jobs_path))
    print(f"Loaded {len(test_jobs)} test jobs")
    
    print(f"\nLoading master resume from: {resume_path}")
    master_resume = load_master_resume(str(resume_path))
    print(f"Master resume loaded ({len(master_resume)} characters)")
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("\n⚠️  WARNING: GEMINI_API_KEY not set")
        return
    
    # Run tests
    all_results = []
    passes = 0
    
    for i, job in enumerate(test_jobs, 1):
        print(f"\n[{i}/{len(test_jobs)}] Processing {job['company']}...")
        result = run_test_for_job(job, master_resume, output_dir)
        all_results.append(result)
        
        if result.get('guardrails', {}).get('passed', False):
            passes += 1
    
    # Summary
    print("\n\n" + "="*80)
    print("GEMINI TEST SUMMARY")
    print("="*80)
    print(f"\nTests completed: {len(all_results)}/{len(test_jobs)}")
    print(f"Guardrails passed: {passes}/{len(all_results)}")
    print(f"\nResults saved to: {output_dir}/")
    print("\n✓ Gemini-only test complete!\n")


if __name__ == "__main__":
    main()
