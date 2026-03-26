"""
Test harness for Phase 1.
Runs test jobs through both Groq and Gemini, generates resumes and emails,
runs guardrails, and produces a comparison report.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
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


def run_test_for_job(job: dict, master_resume: str, provider: str, output_dir: Path):
    """
    Run complete test for a single job with specified provider.
    
    Args:
        job: Job dict from test_jobs.json
        master_resume: Master resume text
        provider: 'groq' or 'gemini'
        output_dir: Directory to save results
    
    Returns:
        Dict with all results
    """
    print(f"\n{'='*80}")
    print(f"Testing: {job['company']} - {job['role']}")
    print(f"Provider: {provider.upper()}")
    print(f"{'='*80}")
    
    results = {
        'job': job,
        'provider': provider,
        'timestamp': datetime.now().isoformat()
    }
    
    # Initialize components
    resume_tailor = ResumeTailor(master_resume)
    email_drafter = EmailDrafter(master_resume)
    guardrails = Guardrails(master_resume)
    
    # Step 1: Generate tailored resume
    print(f"\n[{provider}] Generating tailored resume...")
    resume_result = resume_tailor.tailor_resume(
        job_description=job['description'],
        company=job['company'],
        role=job['role'],
        provider=provider
    )
    results['resume'] = resume_result
    
    if not resume_result['success']:
        print(f"[{provider}] Resume generation FAILED: {resume_result['error']}")
        return results
    
    print(f"[{provider}] Resume generated successfully ({len(resume_result['resume_text'])} chars)")
    
    # Step 2: Generate cold emails
    print(f"[{provider}] Generating cold emails...")
    email_result = email_drafter.draft_emails(
        job_description=job['description'],
        company=job['company'],
        role=job['role'],
        provider=provider
    )
    results['emails'] = email_result
    
    if not email_result['success']:
        print(f"[{provider}] Email generation FAILED: {email_result['error']}")
        return results
    
    print(f"[{provider}] Emails generated successfully")
    
    # Step 3: Run all guardrails
    print(f"[{provider}] Running guardrails...")
    guardrail_results = guardrails.run_all(
        resume_text=resume_result['resume_text'],
        email_hiring_manager=email_result['hiring_manager'],
        email_recruiter=email_result['recruiter'],
        job_description=job['description']
    )
    results['guardrails'] = guardrail_results
    
    # Print guardrail summary
    print(f"\n[{provider}] Guardrail Results:")
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
    
    print(f"\n[{provider}] Overall: {'✓ ALL PASSED' if guardrail_results['passed'] else '✗ FAILED'}")
    
    # Save individual result
    job_safe_name = f"{job['company'].replace(' ', '_')}_{job['role'].replace(' ', '_').replace('/', '_')}"
    output_file = output_dir / f"{job_safe_name}_{provider}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save resume text
    resume_file = output_dir / f"{job_safe_name}_{provider}_resume.txt"
    with open(resume_file, 'w') as f:
        f.write(resume_result['resume_text'])
    
    # Save emails
    email_file = output_dir / f"{job_safe_name}_{provider}_emails.txt"
    with open(email_file, 'w') as f:
        f.write("=== HIRING MANAGER VERSION ===\n")
        f.write(f"Subject: {email_result['hiring_manager']['subject']}\n\n")
        f.write(f"{email_result['hiring_manager']['body']}\n\n")
        f.write("=== RECRUITER VERSION ===\n")
        f.write(f"Subject: {email_result['recruiter']['subject']}\n\n")
        f.write(f"{email_result['recruiter']['body']}\n")
    
    return results


def generate_summary_report(all_results: list, output_dir: Path):
    """Generate SUMMARY.md comparing all results."""
    summary_path = output_dir / "SUMMARY.md"
    
    with open(summary_path, 'w') as f:
        f.write("# Phase 1 Test Results — LLM Output Comparison\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Group results by job
        jobs_dict = {}
        for result in all_results:
            job_id = result['job']['id']
            if job_id not in jobs_dict:
                jobs_dict[job_id] = {}
            jobs_dict[job_id][result['provider']] = result
        
        # Compare each job
        for job_id, providers in jobs_dict.items():
            groq_result = providers.get('groq', {})
            gemini_result = providers.get('gemini', {})
            
            job = groq_result.get('job') or gemini_result.get('job')
            
            f.write(f"## {job['company']} — {job['role']}\n\n")
            f.write(f"**Location:** {job['location']}\n\n")
            
            # Guardrail comparison table
            f.write("### Guardrail Results\n\n")
            f.write("| Guardrail | Groq | Gemini |\n")
            f.write("|-----------|------|--------|\n")
            
            if groq_result and groq_result.get('guardrails'):
                groq_g = groq_result['guardrails']
                gemini_g = gemini_result.get('guardrails', {})
                
                f.write(f"| Hallucination | {'✓' if groq_g['hallucination']['passed'] else '✗'} | {'✓' if gemini_g.get('hallucination', {}).get('passed', False) else '✗'} |\n")
                f.write(f"| Banned Phrases | {'✓' if groq_g['banned_phrases']['passed'] else '✗'} | {'✓' if gemini_g.get('banned_phrases', {}).get('passed', False) else '✗'} |\n")
                f.write(f"| Keyword Match | {groq_g['keyword_match']['score']}% | {gemini_g.get('keyword_match', {}).get('score', 0)}% |\n")
                f.write(f"| Length | {groq_g['length']['char_count']} chars | {gemini_g.get('length', {}).get('char_count', 0)} chars |\n")
                f.write(f"| **Overall** | **{'PASS' if groq_g['passed'] else 'FAIL'}** | **{'PASS' if gemini_g.get('passed', False) else 'FAIL'}** |\n")
            
            f.write("\n### Output Files\n\n")
            job_safe_name = f"{job['company'].replace(' ', '_')}_{job['role'].replace(' ', '_').replace('/', '_')}"
            f.write(f"- Groq resume: `{job_safe_name}_groq_resume.txt`\n")
            f.write(f"- Groq emails: `{job_safe_name}_groq_emails.txt`\n")
            f.write(f"- Gemini resume: `{job_safe_name}_gemini_resume.txt`\n")
            f.write(f"- Gemini emails: `{job_safe_name}_gemini_emails.txt`\n")
            
            f.write("\n---\n\n")
        
        # Overall statistics
        f.write("## Overall Statistics\n\n")
        
        groq_passes = sum(1 for r in all_results if r['provider'] == 'groq' and r.get('guardrails', {}).get('passed', False))
        gemini_passes = sum(1 for r in all_results if r['provider'] == 'gemini' and r.get('guardrails', {}).get('passed', False))
        groq_total = sum(1 for r in all_results if r['provider'] == 'groq')
        gemini_total = sum(1 for r in all_results if r['provider'] == 'gemini')
        
        f.write(f"- **Groq:** {groq_passes}/{groq_total} passed all guardrails\n")
        f.write(f"- **Gemini:** {gemini_passes}/{gemini_total} passed all guardrails\n\n")
        
        # Average keyword match scores
        groq_kw_scores = [r['guardrails']['keyword_match']['score'] 
                         for r in all_results 
                         if r['provider'] == 'groq' and r.get('guardrails')]
        gemini_kw_scores = [r['guardrails']['keyword_match']['score'] 
                           for r in all_results 
                           if r['provider'] == 'gemini' and r.get('guardrails')]
        
        if groq_kw_scores:
            f.write(f"- **Groq avg keyword match:** {sum(groq_kw_scores) / len(groq_kw_scores):.1f}%\n")
        if gemini_kw_scores:
            f.write(f"- **Gemini avg keyword match:** {sum(gemini_kw_scores) / len(gemini_kw_scores):.1f}%\n")
    
    print(f"\n\n{'='*80}")
    print(f"Summary report saved to: {summary_path}")
    print(f"{'='*80}\n")


def main():
    """Run complete test harness."""
    print("="*80)
    print("Phase 1 Test Harness — Resume & Email Generation")
    print("="*80)
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    test_jobs_path = project_root / "tests" / "test_jobs.json"
    resume_path = project_root / "resume.txt"
    output_dir = project_root / "test_output"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Load data
    print(f"\nLoading test jobs from: {test_jobs_path}")
    test_jobs = load_test_jobs(str(test_jobs_path))
    print(f"Loaded {len(test_jobs)} test jobs")
    
    print(f"\nLoading master resume from: {resume_path}")
    master_resume = load_master_resume(str(resume_path))
    print(f"Master resume loaded ({len(master_resume)} characters)")
    
    # Check API keys
    if not os.getenv("GROQ_API_KEY"):
        print("\n⚠️  WARNING: GROQ_API_KEY not set")
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY not set")
    
    # Run tests
    all_results = []
    
    for job in test_jobs:
        # Test with Groq
        groq_result = run_test_for_job(job, master_resume, 'groq', output_dir)
        all_results.append(groq_result)
        
        # Test with Gemini
        gemini_result = run_test_for_job(job, master_resume, 'gemini', output_dir)
        all_results.append(gemini_result)
    
    # Generate summary report
    generate_summary_report(all_results, output_dir)
    
    print("\n✓ Test harness complete!")
    print(f"✓ Results saved to: {output_dir}/")
    print(f"✓ Review SUMMARY.md for side-by-side comparison\n")


if __name__ == "__main__":
    main()
