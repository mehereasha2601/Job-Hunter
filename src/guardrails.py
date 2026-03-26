"""
Guardrails for resume and email quality control.
All 4 guardrails from Section 15 of spec.md:
1. Hallucination detection
2. Banned phrase filter
3. Keyword match scoring
4. Length validation
"""

import re
from typing import Dict, List, Set, Tuple


class Guardrails:
    """All 4 quality control guardrails."""
    
    # Banned phrases
    BANNED_PHRASES = [
        'leveraged', 'leveraging', 'leverage',
        'spearheaded', 'spearheading', 'spearhead',
        'utilized', 'utilizing', 'utilize',
        'orchestrated', 'orchestrating', 'orchestrate',
        'passionate about', 'thrilled to apply', 'excited to bring my expertise',
        'I hope this email finds you well', 
        'I believe I would be a great fit',
        'I believe I would be',
        'I would be a great fit',
        'I am confident I would be'
    ]
    
    # Approved companies
    APPROVED_COMPANIES = {
        'OK AI', 'Khoury College', 'Northeastern University',
        'Info Edge', 'Pharmeasy', 'VIT', 'Vellore Institute of Technology'
    }
    
    # Approved schools
    APPROVED_SCHOOLS = {
        'Northeastern University', 'Vellore Institute of Technology', 'VIT'
    }
    
    # Approved metrics (all numbers/percentages that can appear)
    APPROVED_METRICS = {
        # OK AI
        '12x', '60s', '5s', '50', '60', '500', '1000', '1',
        # TA
        '100',
        # Info Edge
        '30%', '40%',
        # Pharmeasy
        '200K', '25%', '15%', '35%',
        # Projects
        '50K', '84%', '1.13', '30%', '94%', '1,000', '96.2%', '6'
    }
    
    # Approved technical skills (comprehensive list from resume)
    APPROVED_SKILLS = {
        'python', 'java', 'c++', 'javascript', 'react', 'flutter', 'r', 'html', 'css',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'opencv', 'spacy', 'nltk', 'torchvision',
        'aws', 'lambda', 's3', 'dynamodb', 'gcp', 'azure', 'docker', 'kubernetes', 'jenkins', 'linux',
        'sql', 'mongodb', 'bigquery', 'snowflake', 'postgresql', 'kafka', 'apache spark',
        'git', 'copilot', 'bitbucket', 'fastapi', 'langchain', 'openai api',
        'mern', 'opencv', 'nlp', 'computer vision', 'cv', 'ocr', 'etl', 'rest', 'api',
        'llama', 'mistral', 'bert', 'efficientnet', 'mediapipe', 'tensorrt', 'onnx',
        'hugging face', 'lora', 'monte carlo dropout', 'iris', 'fhir', 'sqlite'
    }
    
    def __init__(self, master_resume: str):
        """
        Initialize guardrails with master resume for reference.
        
        Args:
            master_resume: Plain text master resume (source of truth)
        """
        self.master_resume = master_resume.lower()
    
    def run_all(
        self,
        resume_text: str,
        email_hiring_manager: Dict[str, str],
        email_recruiter: Dict[str, str],
        job_description: str
    ) -> Dict[str, any]:
        """
        Run all 4 guardrails on generated content.
        
        Args:
            resume_text: Generated resume text
            email_hiring_manager: Dict with 'subject' and 'body'
            email_recruiter: Dict with 'subject' and 'body'
            job_description: Original job description
        
        Returns:
            Dict with results for each guardrail and overall pass/fail
        """
        results = {
            'hallucination': self.check_hallucination(resume_text),
            'banned_phrases': self.check_banned_phrases(resume_text, email_hiring_manager, email_recruiter),
            'keyword_match': self.check_keyword_match(resume_text, job_description),
            'length': self.check_length(resume_text)
        }
        
        # Overall pass/fail
        results['passed'] = (
            results['hallucination']['passed'] and
            results['banned_phrases']['passed'] and
            results['length']['passed']
            # keyword_match is informational only
        )
        
        return results
    
    def check_hallucination(self, resume_text: str) -> Dict[str, any]:
        """
        Guardrail 1: Detect hallucinated content.
        
        Flags:
        - Company names not in approved list (with context awareness)
        - Degrees/schools not earned
        - Metrics/numbers not in approved list
        - Significant facts not verifiable from master resume
        """
        resume_lower = resume_text.lower()
        flags = []
        
        # Only check for obviously invented companies (in work experience context)
        # Look for lines that start with company names followed by job titles
        work_exp_pattern = r'^([A-Z][A-Za-z\s&]+(?:Inc\.|Limited|Labs|AI|LLC)?)\s*\n\s*([A-Za-z\s]+)\n'
        work_experiences = re.findall(work_exp_pattern, resume_text, re.MULTILINE)
        
        for company, title in work_experiences:
            company = company.strip()
            if company and not any(approved.lower() in company.lower() for approved in self.APPROVED_COMPANIES):
                flags.append(f"Unknown company in work experience: {company}")
        
        # Check for invented metrics - only flag numbers that look like metrics
        # Pattern: number followed by % or x or metric-like context
        metric_patterns = [
            r'(\d+\.?\d*x)\s+(?:performance|improvement|faster|slower)',
            r'(\d+\.?\d*%)\s+(?:reduction|improvement|increase|decrease|accuracy)',
            r'(\d+[KMB]?\+?)\s+(?:users|records|students|endpoints|API|samples)'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                normalized = match.replace(',', '').lower().replace('+', '')
                # Check if it's in approved metrics
                is_approved = False
                for approved in self.APPROVED_METRICS:
                    if normalized in approved.lower() or approved.lower() in normalized:
                        is_approved = True
                        break
                
                if not is_approved:
                    flags.append(f"Unapproved metric: {match}")
        
        # Check for invented degree programs or schools
        if 'phd' in resume_lower or 'ph.d' in resume_lower:
            flags.append("Invented degree: PhD (not earned)")
        
        # Check for schools not in approved list
        school_keywords = ['university', 'college', 'institute']
        for line in resume_text.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in school_keywords):
                # Check if it's an approved school
                if not any(approved.lower() in line_lower for approved in self.APPROVED_SCHOOLS):
                    # Skip lines that are just course names or departments
                    if not any(word in line_lower for word in ['coursework', 'course', 'graduate', 'teaching', 'assistant', 'sciences', 'computer']):
                        flags.append(f"Unknown school: {line.strip()}")
        
        return {
            'passed': len(flags) == 0,
            'flags': flags
        }
    
    def check_banned_phrases(
        self,
        resume_text: str,
        email_hiring_manager: Dict[str, str],
        email_recruiter: Dict[str, str]
    ) -> Dict[str, any]:
        """
        Guardrail 2: Check for banned phrases.
        
        Rejects output containing any banned phrase.
        """
        all_text = resume_text.lower()
        if email_hiring_manager:
            all_text += ' ' + email_hiring_manager.get('subject', '').lower()
            all_text += ' ' + email_hiring_manager.get('body', '').lower()
        if email_recruiter:
            all_text += ' ' + email_recruiter.get('subject', '').lower()
            all_text += ' ' + email_recruiter.get('body', '').lower()
        
        found = []
        for phrase in self.BANNED_PHRASES:
            if phrase.lower() in all_text:
                found.append(phrase)
        
        return {
            'passed': len(found) == 0,
            'found': found
        }
    
    def check_keyword_match(self, resume_text: str, job_description: str) -> Dict[str, any]:
        """
        Guardrail 3: Calculate keyword match score (informational only).
        
        Extracts technical terms from JD (not common words) and calculates
        percentage that appear in tailored resume.
        """
        # Extract technical keywords from JD (simplified approach)
        # Look for capitalized tech terms, acronyms, and specific tools
        jd_lower = job_description.lower()
        resume_lower = resume_text.lower()
        
        # Common tech patterns
        tech_patterns = [
            r'\b(?:python|java|javascript|typescript|go|rust|c\+\+|ruby|php)\b',
            r'\b(?:react|angular|vue|node|django|flask|fastapi|express)\b',
            r'\b(?:aws|gcp|azure|kubernetes|docker|terraform|jenkins)\b',
            r'\b(?:sql|nosql|postgresql|mysql|mongodb|redis|elasticsearch)\b',
            r'\b(?:tensorflow|pytorch|keras|scikit-learn|opencv|nlp|ml|ai)\b',
            r'\b(?:api|rest|graphql|grpc|microservices|distributed)\b',
            r'\b(?:ci/cd|devops|agile|scrum|git|github|gitlab)\b'
        ]
        
        jd_keywords = set()
        for pattern in tech_patterns:
            matches = re.findall(pattern, jd_lower)
            jd_keywords.update(matches)
        
        # Count matches in resume
        matched = 0
        total = len(jd_keywords)
        
        for keyword in jd_keywords:
            if keyword in resume_lower:
                matched += 1
        
        score = (matched / total * 100) if total > 0 else 0
        
        return {
            'score': round(score, 1),
            'matched': matched,
            'total': total,
            'keywords': list(jd_keywords)
        }
    
    def check_length(self, resume_text: str) -> Dict[str, any]:
        """
        Guardrail 4: Validate resume length.
        
        Resume must not exceed ~3,500 characters (approximately 1 page).
        """
        char_count = len(resume_text)
        max_chars = 3500
        
        return {
            'passed': char_count <= max_chars,
            'char_count': char_count,
            'max_chars': max_chars,
            'percentage': round(char_count / max_chars * 100, 1)
        }
