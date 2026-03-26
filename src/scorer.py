"""
LLM-powered job relevance scorer.
Scores jobs 1-10 based on criteria from Section 5 of spec.md.
"""

from typing import Dict, Tuple, List
from src.llm import LLMClient
from src.config import Config
import re


class JobScorer:
    """LLM-powered job relevance scorer."""
    
    def __init__(self, resume_text: str):
        """
        Initialize scorer.
        
        Args:
            resume_text: Candidate's master resume for context
        """
        self.llm = LLMClient()
        self.resume_text = resume_text
    
    def score_job(self, job: Dict) -> Tuple[float, str]:
        """
        Score a job 1-10 based on relevance.
        
        Args:
            job: Job dict with title, company, description, location, h1b_flag, on_target_list
        
        Returns:
            (score, reasoning)
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(job)
        
        try:
            llm_result = self.llm.call(
                user_prompt,
                system_prompt,
                prefer_groq=True  # Use Groq for scoring (fast, good enough)
            )
            
            if not llm_result['success']:
                return 0.0, f"LLM Error: {llm_result['error']}"
            
            response_text = llm_result['text']
            score, reasoning = self._parse_score(response_text)
            
            # Apply location bonus
            score = self._apply_location_bonus(score, job.get('location', ''))
            
            # Cap at 10.0
            score = min(score, 10.0)
            
            return score, reasoning
        
        except Exception as e:
            print(f"Error scoring job {job.get('title')} at {job.get('company')}: {e}")
            return 0.0, f"Error: {str(e)}"
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for scoring."""
        return """You are a job relevance scorer for a software engineer job search.

You will score jobs 1-10 based on how well they match the candidate's background.

Scoring criteria (in priority order):
1. H1B friendliness (30%) - Company on H1B sponsor list, no blocking language
2. Tech stack match (30%) - Python, FastAPI, GCP, ML tools, PyTorch, TensorFlow, backend tech
3. Location (20%) - Boston or Remote preferred
4. Company tier (20%) - On target list of 250 companies

Your task:
- Read the job description carefully
- Compare to the candidate's resume
- Score 1-10 (1=poor match, 10=perfect match)
- Provide brief reasoning (2-3 sentences)

Output format:
SCORE: [number]
REASONING: [2-3 sentences explaining the score]"""
    
    def _build_user_prompt(self, job: Dict) -> str:
        """Build user prompt with job details."""
        title = job.get('title', '')
        company = job.get('company', '')
        location = job.get('location', '')
        description = job.get('description', '')
        h1b_flag = job.get('h1b_flag', 'unknown')
        on_target_list = job.get('on_target_list', False)
        
        # Truncate description if too long
        if len(description) > 3000:
            description = description[:3000] + "..."
        
        return f"""
CANDIDATE RESUME:
{self.resume_text}

---

JOB TO SCORE:

Title: {title}
Company: {company}
Location: {location}
H1B Status: {h1b_flag} (on target list: {on_target_list})

Description:
{description}

---

Score this job 1-10 and explain your reasoning.
"""
    
    def _parse_score(self, response: str) -> Tuple[float, str]:
        """Parse score and reasoning from LLM response."""
        score = 5.0
        reasoning = "No reasoning provided"
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('SCORE:'):
                score_str = line.replace('SCORE:', '').strip()
                # Extract number
                match = re.search(r'(\d+\.?\d*)', score_str)
                if match:
                    score = float(match.group(1))
            
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
        
        return score, reasoning
    
    def _apply_location_bonus(self, base_score: float, location: str) -> float:
        """Apply location bonus to score."""
        location_lower = location.lower()
        
        if 'boston' in location_lower:
            return base_score + Config.LOCATION_BONUS['boston']
        elif 'remote' in location_lower:
            return base_score + Config.LOCATION_BONUS['remote']
        else:
            return base_score + Config.LOCATION_BONUS['other']
    
    def extract_tech_stack(self, description: str) -> List[str]:
        """
        Extract technology keywords from job description.
        
        Args:
            description: Job description text
        
        Returns:
            List of detected technologies
        """
        tech_keywords = [
            # Languages
            'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'sql',
            
            # ML/AI
            'pytorch', 'tensorflow', 'keras', 'scikit-learn', 'hugging face', 'transformers',
            'machine learning', 'deep learning', 'computer vision', 'nlp', 'llm',
            
            # Frameworks
            'fastapi', 'django', 'flask', 'spring', 'react', 'node.js', 'express',
            
            # Cloud
            'aws', 'gcp', 'google cloud', 'azure', 'kubernetes', 'docker', 'terraform',
            
            # Databases
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            
            # Big Data
            'spark', 'hadoop', 'kafka', 'airflow', 'ray',
            
            # DevOps/Tools
            'git', 'jenkins', 'github actions', 'ci/cd', 'prometheus', 'grafana'
        ]
        
        description_lower = description.lower()
        found = []
        
        for tech in tech_keywords:
            if tech.lower() in description_lower:
                found.append(tech)
        
        return found
