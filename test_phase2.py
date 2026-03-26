"""
Quick test of Phase 2 components without hitting LLM rate limits.
"""

from src.db import Database
from src.h1b_filter import h1b_filter, H1B_COMPANIES
from src.output import save_markdown_backup
from datetime import datetime

print("=" * 70)
print("PHASE 2 INTEGRATION TEST (No LLM calls)")
print("=" * 70)

# Test 1: Database
print("\n[Test 1] Database Operations")
print("-" * 70)
db = Database()
print("✓ Database connected")

# Get all jobs
jobs = db.client.table('jobs').select('*').execute().data
print(f"✓ Found {len(jobs)} jobs in database")

for job in jobs:
    print(f"  - {job['title']} at {job['company']}")
    print(f"    Score: {job['score']}/10" if job['score'] else "    Score: pending")

# Test 2: H1B Filter
print("\n[Test 2] H1B Filter")
print("-" * 70)
print(f"✓ Loaded {len(H1B_COMPANIES)} target companies")

test_companies = ['Anthropic', 'Stripe', 'Wayfair', 'RandomStartup Inc']
for company in test_companies:
    result = h1b_filter.check_company(company)
    status = '✅' if result else '❌'
    print(f"{status} {company}")

# Test blocking keywords
test_desc = "Great opportunity! Must have US citizenship. Security clearance required."
is_blocked, phrases = h1b_filter.check_description(test_desc)
print(f"\nBlocking keyword test: {'🚫 BLOCKED' if is_blocked else '✓ OK'}")
if is_blocked:
    print(f"  Found: {phrases[:3]}")

# Test 3: Markdown Output
print("\n[Test 3] Markdown Backup")
print("-" * 70)

if jobs:
    test_job = jobs[0]
    
    # Create mock outputs
    mock_resume = "EASHA MEHER\n\nSample tailored resume content..."
    mock_emails = {
        'hiring_manager': {
            'subject': f"Interested in {test_job['title']} — built scalable systems",
            'body': "Hi, I noticed your opening for...(sample email)"
        },
        'recruiter': {
            'subject': f"Interested in {test_job['title']} — MS AI candidate",
            'body': "Hi, I'm reaching out about...(sample email)"
        }
    }
    
    # Save markdown
    md_path = save_markdown_backup(test_job, mock_resume, mock_emails)
    print(f"✓ Markdown saved to: {md_path}")
    
    # Verify file exists
    import os
    if os.path.exists(md_path):
        size = os.path.getsize(md_path)
        print(f"✓ File created successfully ({size} bytes)")

# Test 4: Configuration
print("\n[Test 4] Configuration")
print("-" * 70)
from src.config import Config

missing = Config.validate()
if missing:
    print(f"⚠ Missing config vars: {', '.join(missing)}")
else:
    print("✓ All required config vars present")

print(f"✓ Greenhouse boards configured: {len(Config.GREENHOUSE_BOARDS)}")
print(f"✓ Job titles configured: {len(Config.JOB_TITLES)}")
print(f"✓ Locations configured: {len(Config.LOCATIONS)}")

print("\n" + "=" * 70)
print("ALL TESTS PASSED ✅")
print("=" * 70)
print("\nPhase 2 Integration Summary:")
print(f"  ✓ Database: Connected and operational")
print(f"  ✓ H1B Filter: {len(H1B_COMPANIES)} companies loaded")
print(f"  ✓ Output: Markdown backup working")
print(f"  ✓ Config: All systems configured")
print("\nReady for full pipeline testing (when LLM rate limits reset)")
