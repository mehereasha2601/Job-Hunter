"""
Cold email drafter.
Follows Section 7 of spec.md:
- Two versions per job (hiring manager + recruiter)
- 5 sentences max
- Subject line: "Interested in [Role] — [quick differentiator]"
- No fluff, sound human
- Banned phrases enforced
"""

from typing import Dict, List
from src.llm import LLMClient


class EmailDrafter:
    """Drafts cold emails for hiring managers and recruiters."""
    
    # Banned phrases (same as resume - keep in sync with guardrails.py)
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
        Initialize with master resume for context.
        
        Args:
            master_resume: Plain text master resume content
        """
        self.master_resume = master_resume
        self.llm = LLMClient()
    
    def draft_emails(
        self,
        job_description: str,
        company: str,
        role: str,
        provider: str = 'gemini'
    ) -> Dict[str, any]:
        """
        Generate both hiring manager and recruiter cold email versions.
        
        Args:
            job_description: Full job description text
            company: Company name
            role: Job title
            provider: 'groq' or 'gemini' (default gemini per spec)
        
        Returns:
            Dict with keys: 'hiring_manager', 'recruiter', 'provider', 'success', 'error'
            Each email is a dict with 'subject' and 'body' keys
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
                'hiring_manager': None,
                'recruiter': None,
                'provider': result['provider'],
                'success': False,
                'error': result['error']
            }
        
        # Parse LLM response
        try:
            emails = self._parse_email_response(result['text'])
            return {
                'hiring_manager': emails['hiring_manager'],
                'recruiter': emails['recruiter'],
                'provider': result['provider'],
                'success': True,
                'error': None
            }
        except Exception as e:
            return {
                'hiring_manager': None,
                'recruiter': None,
                'provider': result['provider'],
                'success': False,
                'error': f'Failed to parse email response: {str(e)}'
            }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for email drafting."""
        return f"""You are an expert at writing cold outreach emails that sound genuinely human.

CANDIDATE BACKGROUND:
{self.master_resume}

RULES:
1. Generate TWO versions per job:
   - Hiring Manager version: More personal, references specific product/mission
   - Recruiter version: More professional, references role fit + qualifications
2. Each email: 5 sentences MAX
3. Subject line format: "Interested in [Role] — [quick differentiator]"
   - Differentiator = concrete detail from candidate's background relevant to JD
   - Examples: "built healthcare CV pipeline at 96% accuracy", "migrated platform to GCP, 12x faster"
4. Lead with genuine interest in company's product/mission + specific role fit
5. No fluff, no "I hope this email finds you well"
6. Clear low-pressure ask (15-min chat)
7. Sound human, not templated
8. BANNED PHRASES - Never use: {', '.join(self.BANNED_PHRASES)}
9. Avoid phrases like: "I believe I would be", "I would be a great fit", "I'm confident I would be"
10. Use confident but humble language: "I think I could", "I'd be excited to", "I'm interested in"

OUTPUT FORMAT (exactly like this):
---HIRING_MANAGER---
SUBJECT: [subject line]
BODY: [email body, 5 sentences max]

---RECRUITER---
SUBJECT: [subject line]
BODY: [email body, 5 sentences max]"""
    
    def _build_user_prompt(self, job_description: str, company: str, role: str) -> str:
        """Build user prompt with job-specific context."""
        return f"""Write cold emails for this job:

COMPANY: {company}
ROLE: {role}

JOB DESCRIPTION:
{job_description}

Generate both versions (hiring manager + recruiter) following the format specified in the system prompt."""
    
    def _parse_email_response(self, response: str) -> Dict[str, Dict[str, str]]:
        """
        Parse LLM response into structured email data.
        
        Args:
            response: Raw LLM response text
        
        Returns:
            Dict with 'hiring_manager' and 'recruiter' keys, each containing 'subject' and 'body'
        """
        # Split by section markers
        sections = response.split('---')
        
        hiring_manager_section = None
        recruiter_section = None
        
        for i, section in enumerate(sections):
            if 'HIRING_MANAGER' in section.upper():
                if i + 1 < len(sections):
                    hiring_manager_section = sections[i + 1]
            elif 'RECRUITER' in section.upper():
                if i + 1 < len(sections):
                    recruiter_section = sections[i + 1]
        
        if not hiring_manager_section or not recruiter_section:
            raise ValueError("Could not find both email sections in response")
        
        def parse_email_section(section: str) -> Dict[str, str]:
            """Parse a single email section into subject and body."""
            lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
            
            subject = ''
            body = ''
            
            for line in lines:
                if line.upper().startswith('SUBJECT:'):
                    subject = line.split(':', 1)[1].strip()
                elif line.upper().startswith('BODY:'):
                    body = line.split(':', 1)[1].strip()
                elif not subject and not body:
                    continue
                elif subject and not body:
                    body = line
                elif body:
                    body += ' ' + line
            
            return {'subject': subject, 'body': body}
        
        return {
            'hiring_manager': parse_email_section(hiring_manager_section),
            'recruiter': parse_email_section(recruiter_section)
        }
