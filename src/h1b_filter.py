"""
H1B sponsorship filter.
Checks job descriptions for blocking language and validates against target list.
Section 4 of spec.md.
"""

import re
from typing import Dict, Tuple, List
from src.config import Config


class H1BFilter:
    """Filter jobs based on H1B sponsorship requirements."""
    
    def __init__(self, target_companies: List[str]):
        """
        Initialize H1B filter.
        
        Args:
            target_companies: List of 250 companies from h1b-companies.md
        """
        self.target_companies = [c.lower() for c in target_companies]
        self.blocking_keywords = [kw.lower() for kw in Config.H1B_BLOCKING_KEYWORDS]
    
    def check_company(self, company: str) -> bool:
        """Check if company is on target list."""
        company_lower = company.lower()
        return any(target in company_lower or company_lower in target for target in self.target_companies)
    
    def check_description(self, description: str) -> Tuple[bool, List[str]]:
        """
        Check job description for H1B blocking language.
        
        Args:
            description: Job description text
        
        Returns:
            (is_blocked, list_of_found_phrases)
        """
        if not description:
            return False, []
        
        description_lower = description.lower()
        found = []
        
        for keyword in self.blocking_keywords:
            if keyword in description_lower:
                found.append(keyword)
        
        is_blocked = len(found) > 0
        return is_blocked, found
    
    def classify_job(self, company: str, description: str) -> Dict:
        """
        Classify job H1B status.
        
        Args:
            company: Company name
            description: Job description
        
        Returns:
            {
                'h1b_flag': 'confirmed' | 'unknown' | 'blocked',
                'on_target_list': bool,
                'blocking_phrases': list
            }
        """
        on_target_list = self.check_company(company)
        is_blocked, blocking_phrases = self.check_description(description)
        
        if is_blocked:
            h1b_flag = 'blocked'
        elif on_target_list:
            h1b_flag = 'confirmed'
        else:
            h1b_flag = 'unknown'
        
        return {
            'h1b_flag': h1b_flag,
            'on_target_list': on_target_list,
            'blocking_phrases': blocking_phrases
        }


def load_h1b_companies(filepath: str = 'h1b-companies.md') -> List[str]:
    """
    Parse h1b-companies.md and extract all company names.
    
    Args:
        filepath: Path to h1b-companies.md
    
    Returns:
        List of company names
    """
    companies = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract companies from numbered lists
    # Pattern: "123. ⭐CompanyName, 124. CompanyName"
    pattern = r'\d+\.\s*(?:⭐)?\s*([^,\n]+)'
    matches = re.findall(pattern, content)
    
    for match in matches:
        # Clean up company name
        company = match.strip()
        # Remove notes in parentheses
        company = re.sub(r'\s*\([^)]*\)', '', company)
        # Remove stars
        company = company.replace('⭐', '')
        company = company.strip()
        
        if company and len(company) > 1:
            companies.append(company)
    
    return companies


# Initialize global filter with target companies
try:
    H1B_COMPANIES = load_h1b_companies()
    h1b_filter = H1BFilter(H1B_COMPANIES)
except Exception as e:
    print(f"Warning: Could not load H1B companies: {e}")
    h1b_filter = None
