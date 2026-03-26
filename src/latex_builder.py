"""
LaTeX resume builder.
Converts plain text tailored resume to LaTeX and generates PDF.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List


class LatexBuilder:
    """Builds LaTeX resume from plain text and generates PDF."""
    
    def __init__(self, template_path: str):
        """
        Initialize with LaTeX template.
        
        Args:
            template_path: Path to resume.tex template
        """
        with open(template_path, 'r') as f:
            self.template = f.read()
    
    def build_pdf(
        self,
        resume_text: str,
        output_dir: str,
        company: str,
        role: str
    ) -> Dict[str, any]:
        """
        Generate PDF from plain text resume.
        
        Args:
            resume_text: Plain text tailored resume
            output_dir: Directory to save PDF
            company: Company name
            role: Job title
        
        Returns:
            Dict with 'success', 'pdf_path', 'error'
        """
        try:
            # Parse resume into sections
            parsed = self._parse_resume(resume_text)
            
            # Fill template
            latex_content = self._fill_template(parsed)
            
            # Save .tex file
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            filename = f"Resume_{company.replace(' ', '_')}_{role.replace(' ', '_').replace('/', '_')}"
            tex_file = output_path / f"{filename}.tex"
            
            with open(tex_file, 'w') as f:
                f.write(latex_content)
            
            # Compile to PDF (requires pdflatex installed)
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(output_path), str(tex_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            pdf_file = output_path / f"{filename}.pdf"
            
            if pdf_file.exists():
                return {
                    'success': True,
                    'pdf_path': str(pdf_file),
                    'tex_path': str(tex_file),
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'pdf_path': None,
                    'tex_path': str(tex_file),
                    'error': f"PDF not generated. LaTeX output: {result.stderr[:500]}"
                }
        
        except FileNotFoundError:
            return {
                'success': False,
                'pdf_path': None,
                'tex_path': None,
                'error': 'pdflatex not found. Install with: brew install basictex (or apt-get install texlive-latex-base)'
            }
        except Exception as e:
            return {
                'success': False,
                'pdf_path': None,
                'tex_path': None,
                'error': str(e)
            }
    
    def _parse_resume(self, resume_text: str) -> Dict[str, any]:
        """Parse plain text resume into structured data."""
        lines = resume_text.split('\n')
        
        parsed = {
            'header': {},
            'education': [],
            'skills': {},
            'experience': [],
            'projects': []
        }
        
        # Parse header (first 3 lines)
        if len(lines) >= 3:
            parsed['header']['name'] = lines[0].strip()
            header_line = lines[1].strip()
            links_line = lines[2].strip()
            
            # Extract contact info
            parts = header_line.split()
            parsed['header']['email'] = parts[0] if len(parts) > 0 else ''
            parsed['header']['phone'] = parts[1] if len(parts) > 1 else ''
            parsed['header']['location'] = ' '.join(parts[2:]) if len(parts) > 2 else ''
            
            # Extract links
            links = links_line.split()
            parsed['header']['linkedin'] = links[0] if len(links) > 0 else ''
            parsed['header']['github'] = links[1] if len(links) > 1 else ''
            parsed['header']['website'] = links[2] if len(links) > 2 else ''
        
        # Parse sections (simplified - just return the text for now)
        parsed['full_text'] = resume_text
        
        return parsed
    
    def _fill_template(self, parsed: Dict) -> str:
        """Fill LaTeX template with parsed resume data."""
        latex = self.template
        
        # For now, use a simple approach - just escape special chars
        # Full parsing can be added later
        
        # Escape LaTeX special characters
        def escape_latex(text: str) -> str:
            chars = {
                '&': r'\&',
                '%': r'\%',
                '$': r'\$',
                '#': r'\#',
                '_': r'\_',
                '{': r'\{',
                '}': r'\}',
                '~': r'\textasciitilde{}',
                '^': r'\^{}',
                '\\': r'\textbackslash{}'
            }
            for char, escaped in chars.items():
                text = text.replace(char, escaped)
            return text
        
        # Simple placeholder replacement
        latex = latex.replace('{{NAME}}', parsed['header'].get('name', 'Name'))
        latex = latex.replace('{{EMAIL}}', parsed['header'].get('email', 'email'))
        latex = latex.replace('{{PHONE}}', parsed['header'].get('phone', 'phone'))
        latex = latex.replace('{{LOCATION}}', parsed['header'].get('location', 'location'))
        latex = latex.replace('{{LINKEDIN}}', parsed['header'].get('linkedin', 'linkedin'))
        latex = latex.replace('{{GITHUB}}', parsed['header'].get('github', 'github'))
        latex = latex.replace('{{WEBSITE}}', parsed['header'].get('website', 'website'))
        
        # For sections, we'll need proper parsing in Phase 2
        # For now, just note that full parsing is needed
        latex = latex.replace('{{EDUCATION_ENTRIES}}', '% TODO: Parse education')
        latex = latex.replace('{{TECHNICAL_SKILLS}}', '% TODO: Parse skills')
        latex = latex.replace('{{WORK_EXPERIENCE_ENTRIES}}', '% TODO: Parse experience')
        latex = latex.replace('{{PROJECT_ENTRIES}}', '% TODO: Parse projects')
        
        return latex
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}'
        }
        for char, escaped in chars.items():
            text = text.replace(char, escaped)
        return text
