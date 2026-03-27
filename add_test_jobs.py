"""
Add some real test jobs to database for testing the pipeline.
"""

from src.db import Database
from src.h1b_filter import h1b_filter

db = Database()

# Add realistic job postings
test_jobs = [
    {
        'title': 'AI/ML Engineer',
        'company': 'Scale AI',
        'url': 'https://boards.greenhouse.io/scaleai/jobs/4401234',
        'source': 'greenhouse',
        'description': '''Scale AI is looking for an AI/ML Engineer to build infrastructure for our data engine.

Requirements:
- MS or PhD in Computer Science, Machine Learning, or related field
- 3+ years experience with Python and ML frameworks (PyTorch, TensorFlow)
- Experience with large-scale distributed systems
- Strong understanding of computer vision or NLP

You will:
- Design and implement ML training pipelines
- Build evaluation frameworks for ML models
- Work with our research team on model improvements
- Deploy models to production at scale

Tech stack: Python, PyTorch, Kubernetes, GCP, Ray''',
        'location': 'San Francisco, CA',
        'h1b_flag': 'confirmed',
        'on_target_list': True
    },
    {
        'title': 'Backend Software Engineer',
        'company': 'Databricks',
        'url': 'https://boards.greenhouse.io/databricks/jobs/5502345',
        'source': 'greenhouse',
        'description': '''Databricks is hiring Backend Engineers to work on our data lakehouse platform.

Requirements:
- BS/MS in Computer Science or equivalent
- 5+ years backend development experience
- Expert in Java, Scala, or Python
- Experience with distributed systems (Spark, Kafka)
- Strong database knowledge (PostgreSQL, Cassandra)

You will:
- Build scalable APIs for data processing
- Optimize query performance for petabyte-scale data
- Design fault-tolerant distributed systems
- Collaborate with ML teams on feature development

Tech stack: Scala, Python, Apache Spark, Kubernetes, AWS''',
        'location': 'Remote',
        'h1b_flag': 'confirmed',
        'on_target_list': True
    },
    {
        'title': 'Full Stack Engineer',
        'company': 'Klaviyo',
        'url': 'https://boards.greenhouse.io/klaviyo/jobs/6603456',
        'source': 'greenhouse',
        'description': '''Join Klaviyo's product team to build customer data platform features.

Requirements:
- 3+ years full stack development
- Strong Python backend experience (Django/FastAPI)
- Frontend skills (React, TypeScript)
- Experience with PostgreSQL and Redis
- AWS experience preferred

You will:
- Build customer-facing features for marketing automation
- Design RESTful APIs serving millions of requests
- Optimize database queries and caching
- Work closely with product and design teams

Tech stack: Python, FastAPI, React, PostgreSQL, Redis, AWS''',
        'location': 'Boston, MA',
        'h1b_flag': 'confirmed',
        'on_target_list': True
    }
]

print('Adding test jobs to database...\n')

for job in test_jobs:
    result = db.insert_job(job)
    print(f'✓ Added: {job["title"]} at {job["company"]}')
    print(f'  ID: {result["id"][:24]}...')
    print(f'  Status: {result["status"]}, Score: {result["score"]}')
    print()

print(f'✓ Added {len(test_jobs)} test jobs')
print('\nNow run Step 1 again to score these jobs:')
print('  Go to: https://github.com/mehereasha2601/Job-Hunter/actions')
print('  Click "Step 1 - Score Jobs & Send Digest" → "Run workflow"')
