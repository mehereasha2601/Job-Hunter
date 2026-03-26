"""
Cover letter generator.
Only generates when job description explicitly requires a cover letter.
Section 8 of spec.md.
"""

from typing import Dict, Optional
from src.llm import LLMClient


class CoverLetterGenerator:
    """Generates cover letters when required by job description."""
    
    # Banned phrases (same as resume + emails)
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
    
    def __init__(self, master_resume: str):
        """
        Initialize cover letter generator.
        
        Args:
            master_resume: Candidate's master resume text
        """
        self.master_resume = master_resume
        self.llm = LLMClient()
    
    def check_if_required(self, job_description: str) -> bool:
        """
        Check if job description explicitly requires a cover letter.
        
        Args:
            job_description: Full job description text
        
        Returns:
            True if cover letter is required
        """
        description_lower = job_description.lower()
        
        # Keywords indicating cover letter requirement
        required_keywords = [
            'cover letter required',
            'cover letter is required',
            'must include cover letter',
            'please submit a cover letter',
            'cover letter must',
            'attach a cover letter',
            'application must include',
            'along with your resume, please submit'
        ]
        
        for keyword in required_keywords:
            if keyword in description_lower:
                return True
        
        return False
    
    def generate(
        self,
        job_description: str,
        company: str,
        role: str,
        provider: str = 'gemini'
    ) -> Dict[str, any]:
        """
        Generate cover letter for job.
        
        Args:
            job_description: Full job description text
            company: Company name
            role: Job title
            provider: 'groq' or 'gemini'
        
        Returns:
            Dict with keys: 'cover_letter', 'provider', 'success', 'error'
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(job_description, company, role)
        
        prefer_groq = (provider == 'groq')
        result = self.llm.call(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=2048,
            prefer_groq=prefer_groq
        )
        
        if not result['success']:
            return {
                'cover_letter': '',
                'provider': result['provider'],
                'success': False,
                'error': result['error']
            }
        
        cover_letter = result['text'].strip()
        
        # Validate no banned phrases
        cover_lower = cover_letter.lower()
        found_banned = [phrase for phrase in self.BANNED_PHRASES if phrase in cover_lower]
        
        if found_banned:
            return {
                'cover_letter': cover_letter,
                'provider': result['provider'],
                'success': False,
                'error': f"Contains banned phrases: {', '.join(found_banned)}"
            }
        
        return {
            'cover_letter': cover_letter,
            'provider': result['provider'],
            'success': True,
            'error': None
        }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for cover letter generation."""
        return f"""You are writing a cover letter for a job application.

MASTER RESUME (for context):
{self.master_resume}

COVER LETTER RULES:
1. 3-4 short paragraphs max
2. Same tone as cold emails: conversational, human, specific
3. Structure:
   - Para 1: Why you're interested in THIS company specifically (reference their product/mission)
   - Para 2: Connect your relevant experience to the role (2-3 specific examples with metrics)
   - Para 3: Close with enthusiasm and clear next step
4. Sound like a real person, not a template
5. No fluff or filler
6. BANNED PHRASES (never use):
   - leveraged, spearheaded, utilized, orchestrated
   - passionate about, thrilled to apply, excited to bring
   - I hope this finds you well
   - I believe I would be a great fit

OUTPUT: Just the cover letter text, no subject line needed."""
    
    def _build_user_prompt(self, job_description: str, company: str, role: str) -> str:
        """Build user prompt with job details."""
        return f"""Generate a cover letter for this job:

COMPANY: {company}
ROLE: {role}

JOB DESCRIPTION:
{job_description}

Write a 3-4 paragraph cover letter that:
- Shows genuine interest in {company}'s work/product
- Highlights 2-3 relevant experiences with specific metrics from the resume
- Sounds conversational and human, not templated
- Closes with enthusiasm and a clear ask
- Contains ZERO banned phrases

OUTPUT FORMAT: Just the cover letter text (no "Dear Hiring Manager" salutation needed, start directly with content).
"""
