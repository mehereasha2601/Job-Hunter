"""
Central configuration for job hunter pipeline.
All settings, API keys, and constants in one place.
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class."""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    APIFY_TOKEN = os.getenv("APIFY_TOKEN")
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Google
    GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
    RESUME_GOOGLE_DOC_ID = os.getenv("RESUME_GOOGLE_DOC_ID")
    
    # Email
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
    
    # GitHub
    GH_PAT = os.getenv("GH_PAT")
    UI_PASSWORD = os.getenv("UI_PASSWORD")
    
    # LLM Settings
    LLM_TEMPERATURE = 0.3
    LLM_MAX_TOKENS = 4096
    
    # Greenhouse Board URLs (Top 40 from spec Section 3)
    GREENHOUSE_BOARDS = {
        # National companies
        'Anthropic': 'https://boards.greenhouse.io/anthropic',
        'Scale AI': 'https://boards.greenhouse.io/scaleai',
        'Databricks': 'https://boards.greenhouse.io/databricks',
        'Perplexity': 'https://boards.greenhouse.io/perplexityai',
        'Stripe': 'https://boards.greenhouse.io/stripe',
        'Cloudflare': 'https://boards.greenhouse.io/cloudflare',
        'Datadog': 'https://boards.greenhouse.io/datadog',
        'Ramp': 'https://boards.greenhouse.io/ramp',
        'Flatiron Health': 'https://boards.greenhouse.io/flatiron',
        'MongoDB': 'https://boards.greenhouse.io/mongodb',
        'Snowflake': 'https://boards.greenhouse.io/snowflake',
        'Confluent': 'https://boards.greenhouse.io/confluent',
        'Twilio': 'https://boards.greenhouse.io/twilio',
        'Airbnb': 'https://boards.greenhouse.io/airbnb',
        'DoorDash': 'https://boards.greenhouse.io/doordash',
        'Pinterest': 'https://boards.greenhouse.io/pinterest',
        'Figma': 'https://boards.greenhouse.io/figma',
        'Notion': 'https://boards.greenhouse.io/notion',
        'Duolingo': 'https://boards.greenhouse.io/duolingo',
        'Grammarly': 'https://boards.greenhouse.io/grammarly',
        'HubSpot': 'https://boards.greenhouse.io/hubspot',
        'GitLab': 'https://boards.greenhouse.io/gitlab',
        'Fivetran': 'https://boards.greenhouse.io/fivetran',
        'dbt Labs': 'https://boards.greenhouse.io/dbtlabs',
        'Pinecone': 'https://boards.greenhouse.io/pinecone',
        'Together AI': 'https://boards.greenhouse.io/togetherai',
        'Robinhood': 'https://boards.greenhouse.io/robinhood',
        'Plaid': 'https://boards.greenhouse.io/plaid',
        'Wiz': 'https://boards.greenhouse.io/wiz',
        'Grafana Labs': 'https://boards.greenhouse.io/grafanalabs',
        
        # Boston companies
        'Klaviyo': 'https://boards.greenhouse.io/klaviyo',
        'Wayfair': 'https://boards.greenhouse.io/wayfair',
        'Toast': 'https://boards.greenhouse.io/toast',
        'Chewy': 'https://boards.greenhouse.io/chewy',
        'CarGurus': 'https://boards.greenhouse.io/cargurus',
        'DataRobot': 'https://boards.greenhouse.io/datarobot',
        'Athenahealth': 'https://boards.greenhouse.io/athenahealth',
        'Foundation Medicine': 'https://boards.greenhouse.io/foundationmedicine',
        'Whoop': 'https://boards.greenhouse.io/whoop',
        'Benchling': 'https://boards.greenhouse.io/benchling'
    }
    
    # Job search parameters (Section 4)
    JOB_TITLES = [
        'Software Engineer',
        'ML Engineer',
        'AI Engineer',
        'Machine Learning Engineer',
        'Backend Engineer',
        'Full Stack Engineer'
    ]
    
    # Exclude senior roles (Section 4 - Entry/Mid level only)
    EXCLUDE_SENIORITY_KEYWORDS = [
        'senior',
        'sr.',
        'staff',
        'principal',
        'lead',
        'director',
        'vp',
        'vice president',
        'head of',
        'chief',
        '5+ years',
        '5 years',
        '6+ years',
        '7+ years',
        '8+ years'
    ]
    
    LOCATIONS = [
        'Boston, MA',
        'Remote',
        'United States'
    ]
    
    # US location keywords (must contain at least one)
    US_LOCATION_KEYWORDS = [
        'united states',
        'usa',
        'us',
        'remote',
        'boston',
        'san francisco',
        'new york',
        'seattle',
        'austin',
        'denver',
        'chicago',
        'los angeles',
        'california',
        'massachusetts',
        'washington',
        'texas',
        'colorado'
    ]
    
    # H1B filter keywords (Section 4)
    H1B_BLOCKING_KEYWORDS = [
        'us citizen',
        'us citizenship required',
        'citizenship required',
        'no sponsorship',
        'will not sponsor',
        'cannot sponsor',
        'security clearance',
        'clearance required',
        'must be a us person',
        'itar',
        'must be authorized to work',
        'must be legally authorized',
        'us work authorization required'
    ]
    
    # Location scoring bonuses (Section 5)
    LOCATION_BONUS = {
        'boston': 2,
        'remote': 1,
        'other': 0
    }
    
    # Dedup window (Section 13)
    DEDUP_WINDOW_DAYS = 30
    
    # Job filtering
    MAX_JOB_AGE_DAYS = 2  # Only jobs posted in last 2 days (48 hours)
    
    # Rate limit thresholds (Section 16)
    RATE_LIMIT_WARNING_THRESHOLD = 0.20  # 20%
    
    # Resume constraints
    MAX_RESUME_CHARS = 3500
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of missing required vars."""
        missing = []
        
        # Phase 1 required
        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        
        # Phase 2 required
        if not cls.SUPABASE_URL:
            missing.append("SUPABASE_URL (Phase 2)")
        if not cls.SUPABASE_KEY:
            missing.append("SUPABASE_KEY (Phase 2)")
        
        return missing
