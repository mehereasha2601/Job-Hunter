"""
Resume tailoring engine.
Follows strict rules from Section 6 of spec.md:
- STRICTLY 1 page (under 3500 chars)
- All 4 work experiences ALWAYS included
- Only approved metrics allowed
- Banned phrases enforced
- Natural, conversational tone
"""

from typing import Dict, List, Optional
from src.llm import LLMClient


class ResumeTailor:
    """Tailors resume to job descriptions while maintaining strict quality controls."""
    
    # Approved metrics only (Section 6)
    APPROVED_METRICS = {
        'OK AI': [
            '12x performance improvement (60s → 5s response times)',
            '50-60 API endpoints built',
            '500-1000 users/candidates served',
            'Migrated 1 microservice to GCP'
        ],
        'TA Role': [
            'Supported ~100 students per semester',
            '1 lab session per week'
        ],
        'Info Edge': [
            '30% reduction in false positives',
            '40% reduction in manual review time'
        ],
        'Pharmeasy': [
            '200K+ medical records processed monthly',
            '25% reduction in processing time',
            '15% improvement in medicine mapping accuracy',
            '35% reduction in manual review time'
        ],
        'KidneyCare': [
            '96.2% CV pipeline accuracy',
            '6 team members',
            'Full stack: toilet-mounted camera, CV pipeline, FastAPI backend, InterSystems IRIS FHIR, React frontend'
        ]
    }
    
    # Banned phrases
    BANNED_PHRASES = [
        'leveraged', 'leveraging', 'leverage',
        'spearheaded', 'spearheading', 'spearhead',
        'utilized', 'utilizing', 'utilize',
        'orchestrated', 'orchestrating', 'orchestrate',
        'passionate about', 'thrilled to apply', 'excited to bring my expertise',
        'I hope this email finds you well', 'I believe I would be a great fit'
    ]
    
    def __init__(self, master_resume: str):
        """
        Initialize with master resume content.
        
        Args:
            master_resume: Plain text master resume content
        """
        self.master_resume = master_resume
        self.llm = LLMClient()
    
    def tailor_resume(
        self,
        job_description: str,
        company: str,
        role: str,
        provider: str = 'gemini'  # Changed from 'groq' - Gemini performs better for tailoring
    ) -> Dict[str, any]:
        """
        Generate tailored resume for a specific job.
        
        Args:
            job_description: Full job description text
            company: Company name
            role: Job title
            provider: 'groq' or 'gemini'
        
        Returns:
            Dict with keys: 'resume_text', 'provider', 'success', 'error'
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(job_description, company, role)
        
        prefer_groq = (provider == 'groq')
        result = self.llm.call(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=4096,
            prefer_groq=prefer_groq
        )
        
        if result['success']:
            return {
                'resume_text': result['text'],
                'provider': result['provider'],
                'success': True,
                'error': None
            }
        else:
            return {
                'resume_text': '',
                'provider': result['provider'],
                'success': False,
                'error': result['error']
            }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with all resume rules."""
        return f"""You are an expert resume writer. Your job is to tailor a resume to a specific job description while following STRICT rules.

MASTER RESUME (source of truth):
{self.master_resume}

CRITICAL RULES:
1. STRICTLY 1 PAGE MAX - Keep output under 3,500 characters total
2. ALL 4 WORK EXPERIENCES MUST ALWAYS BE INCLUDED:
   - OK AI (ML Intern, Sep 2025 – Jan 2026)
   - Khoury College TA (Sep 2024 – Aug 2025)
   - Info Edge (Senior Software Developer, Jul 2023 – Dec 2023)
   - Pharmeasy (Software Developer, Jul 2021 – Jul 2023)
3. NEVER invent metrics - only use these approved metrics:
   {self._format_approved_metrics()}
4. BANNED PHRASES - Never use: {', '.join(self.BANNED_PHRASES)}
5. STRUCTURE (fixed order):
   - Header (name, email, phone, location, LinkedIn, GitHub, website)
   - Education (Northeastern MS first, VIT B.Tech second)
   - Technical Skills (5 categories: Languages & Frameworks, ML & AI, Cloud & DevOps, Database & Big Data, Tools & Platforms)
   - Work Experience (all 4 always included)
   - Projects & Leadership (2 current projects + optional 1 swap)

TAILORING INSTRUCTIONS:
- Reorder coursework items to match JD keywords
- Reorder skills within each category to put JD-relevant ones first
- Rephrase bullet points to mirror JD keywords (but stay truthful)
- PRESERVE STAR FORMAT (Situation, Task, Action, Result) in work experience bullets
- PRESERVE ALL metrics and quantifiable results from original resume
- Include 3-5 bullets per work experience - aim to keep as many original bullets as possible
- Prioritize bullets with specific metrics and measurable impact
- Only condense if absolutely needed to stay under 3,500 chars (you have room - use it!)
- Each bullet should include: context/situation, specific technologies used, and quantifiable result
- Section order stays fixed (never reorder sections)

PROJECT SWAP RULES:
- Always keep: Bayesian Uncertainty QA, Cricket Shot Recognition
- May swap in max 1 additional project if space permits:
  - KidneyCare (primary swap candidate - healthcare CV, FastAPI, 96.2% accuracy)
  - Mindful Monitor (health tech roles ONLY)
- If swapping, condense least relevant of the 2 existing projects to make room

TONE:
- Conversational but polished - sound like a real person
- Natural verbs: built, designed, created, improved, ran
- No AI-generated phrasing or corporate jargon
- Professional but warm

NEVER MENTION:
- Visa status
- Sponsorship needs
- Summary/objective sections

OUTPUT FORMAT:
Plain text resume, ready to be formatted. Use clear section headers."""
    
    def _format_approved_metrics(self) -> str:
        """Format approved metrics for prompt."""
        lines = []
        for company, metrics in self.APPROVED_METRICS.items():
            lines.append(f"   {company}:")
            for metric in metrics:
                lines.append(f"     - {metric}")
        return '\n'.join(lines)
    
    def _build_user_prompt(self, job_description: str, company: str, role: str) -> str:
        """Build user prompt with job-specific context."""
        return f"""Tailor the master resume for this job application:

COMPANY: {company}
ROLE: {role}

JOB DESCRIPTION:
{job_description}

Generate a tailored resume that:
1. **MUST stay under 3,500 characters** (CRITICAL - this is non-negotiable)
2. Includes all 4 work experiences (never remove any)
3. Reorders coursework and skills to match the JD keywords
4. For work experience bullets:
   - Preserve STAR format (Situation/Task, Action, Result) with specific metrics
   - Include 3-5 bullets per experience, BUT prioritize staying under 3,500 chars
   - If needed to fit: Keep the most impactful bullets with metrics, condense others
   - Always include bullets that have quantifiable results (12x, 30%, 200K+, etc.)
5. For projects: 
   - Keep 2-3 bullets per project with key metrics (84%, 94%, 96.2%)
   - If space is tight, use 1-2 bullets per project
6. Decides whether to swap in KidneyCare project (if healthcare/CV/FastAPI relevant)
7. Sounds natural and human, not templated
8. Contains zero banned phrases
9. Uses only approved metrics (no invented numbers)

CRITICAL LENGTH STRATEGY:
- Start with all content, then cut back if needed
- Priority order: metrics > technical details > context
- If you're at 3,400+ chars, remove least relevant bullets
- Better to have 3 strong bullets per job than 5 weak ones
- The 3,500 char limit is HARD - exceeding it fails the guardrail

Example good bullet:
"Built backend services processing 200K+ medical records monthly using Python and Java, with PostgreSQL and AWS infrastructure, ensuring data integrity and healthcare compliance."

Output the complete tailored resume as plain text."""
