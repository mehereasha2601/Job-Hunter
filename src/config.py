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
        # Core engineering roles
        'Software Engineer',
        'ML Engineer',
        'AI Engineer',
        'Machine Learning Engineer',
        'Backend Engineer',
        'Frontend Engineer',
        'Full Stack Engineer',
        'API Engineer',  # Backend / API Engineer
        'SDK Engineer',  # SDK development roles
        # Additional ML/AI roles
        'Data Engineer',
        'Machine Learning Scientist',
        'Research Scientist',
        'Applied Scientist',
        'NLP Engineer',
        'Natural Language Processing Engineer',
        'Computer Vision Engineer',
        'Data Scientist',
        # Platform roles
        'Platform Engineer',
        'Infrastructure Engineer',
        'MLOps Engineer',
        'ML Platform Engineer',
        # Entry-level variants
        'New Grad Software Engineer',
        'New Grad',
        'Associate Engineer',
        'Associate Software Engineer',
        'Junior Engineer',
        'Junior Software Engineer',
        # QA/Testing roles
        'Test Engineer',
        'QA Engineer',
        'SDET',
        'Software Development Engineer in Test',
        # Analyst roles (relevant to data/ML)
        'Data Analyst',
        'ML Analyst',
        'AI Analyst'
    ]
    
    # Exclude senior roles (Section 4 - Entry/Mid level only)
    EXCLUDE_SENIORITY_KEYWORDS = [
        'senior',
        'sr.',
        'sr ',
        'staff',
        'principal',
        'lead',
        'director',
        'vp',
        'vice president',
        'head of',
        'chief',
        'manager',  # Added to exclude manager roles
        'engineering manager',
        '3+ years',
        '3 years',
        '4+ years',
        '4 years',
        '5+ years',
        '5 years',
        '6+ years',
        '7+ years',
        '8+ years',
        '10+ years'
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
        'us-',  # US-SF, US-NYC, US-Remote
        ', us',  # "San Francisco, US"
        'remote in us',
        'remote us',
        'us remote',
        'us,',  # "NYC, US, Canada"
        'nyc',
        'new york',
        'san francisco',
        'sf,',  # "SF, NYC"
        'seattle',
        'sea,',  # "SEA, SF"
        'boston',
        'austin',
        'denver',
        'chicago',
        'chi,',  # "CHI, NYC"
        'los angeles',
        'california',
        'massachusetts',
        'washington',
        'texas',
        'colorado',
        'portland',
        'miami',
        'atlanta',
        'philadelphia',
        'washington dc'
    ]
    
    # Exclude non-US locations
    NON_US_LOCATION_KEYWORDS = [
        'canada',
        'toronto',
        'vancouver',
        'montreal',
        'can-',  # CAN-Remote
        'dublin',
        'london',
        'berlin',
        'paris',
        'singapore',
        'bengaluru',
        'bangalore',
        'india',
        'tokyo',
        'mexico',
        'brazil',
        'germany',
        'france',
        'uk',
        'ireland',
        'australia',
        'sydney',
        'melbourne',
        'japan',
        'korea',
        'china',
        'hong kong'
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
    MAX_JOB_AGE_DAYS = 14  # Last 14 days for Greenhouse (has reliable dates)
    LINKEDIN_HOURS_OLD = 24  # Last 24 hours for LinkedIn scraping (JobSpy, Apify)
    
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
