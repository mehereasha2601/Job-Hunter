"""
Email notifier using Gmail SMTP.
Sends digest emails (Step 1) and completion notifications (Step 2).
Section 9 and 10 of spec.md.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from datetime import datetime

from src.config import Config


def send_digest_email(jobs: List[Dict]) -> Dict:
    """
    Send digest email with high-scoring jobs.
    
    Args:
        jobs: List of scored jobs (7.0+)
    
    Returns:
        {'success': bool, 'error': str or None}
    """
    try:
        # Build email content
        subject = f"Job Digest — {len(jobs)} high-scoring matches — {datetime.now().strftime('%b %d, %Y')}"
        html_body = _build_digest_html(jobs)
        
        # Send email
        result = _send_email(
            to_email=Config.NOTIFICATION_EMAIL,
            subject=subject,
            html_body=html_body
        )
        
        return result
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def send_tailor_complete_email(jobs: List[Dict]) -> Dict:
    """
    Send completion email after Step 2 with links to all docs.
    
    Args:
        jobs: List of tailored jobs with doc links
    
    Returns:
        {'success': bool, 'error': str or None}
    """
    try:
        subject = f"Tailored resumes ready — {len(jobs)} jobs — {datetime.now().strftime('%b %d, %Y')}"
        html_body = _build_completion_html(jobs)
        
        result = _send_email(
            to_email=Config.NOTIFICATION_EMAIL,
            subject=subject,
            html_body=html_body
        )
        
        return result
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _send_email(to_email: str, subject: str, html_body: str) -> Dict:
    """
    Send HTML email via Gmail SMTP.
    
    Args:
        to_email: Recipient email
        subject: Email subject
        html_body: HTML body content
    
    Returns:
        {'success': bool, 'error': str or None}
    """
    try:
        if not Config.GMAIL_APP_PASSWORD:
            return {'success': False, 'error': 'GMAIL_APP_PASSWORD not configured'}
        
        if not to_email:
            return {'success': False, 'error': 'NOTIFICATION_EMAIL not configured'}
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = to_email  # Sending to self
        msg['To'] = to_email
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(to_email, Config.GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        return {'success': True, 'error': None}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _build_digest_html(jobs: List[Dict]) -> str:
    """Build HTML for digest email."""
    
    # Sort by score descending
    sorted_jobs = sorted(jobs, key=lambda j: -j.get('score', 0))
    
    job_rows = []
    
    for job in sorted_jobs:
        score = job.get('score', 0)
        title = job.get('title', 'Unknown Title')
        company = job.get('company', 'Unknown Company')
        location = job.get('location', 'Unknown Location')
        url = job.get('url', '#')
        description = job.get('description', '')[:500]
        tech_stack = ', '.join(job.get('tech_stack', [])[:8])
        h1b_flag = job.get('h1b_flag', 'unknown')
        on_target_list = job.get('on_target_list', False)
        
        # H1B emoji
        if h1b_flag == 'confirmed':
            h1b_emoji = '✅ Confirmed sponsor'
        elif h1b_flag == 'blocked':
            h1b_emoji = '❌ Blocked'
        else:
            h1b_emoji = '⚠️ Unknown'
        
        # Target list indicator
        target_indicator = '⭐ On target list' if on_target_list else ''
        
        job_html = f"""
        <div style="border: 1px solid #ddd; padding: 16px; margin-bottom: 20px; border-radius: 8px;">
            <h3 style="margin: 0 0 8px 0; color: #333;">
                <span style="background: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px; margin-right: 8px; font-size: 14px;">
                    {score:.1f}/10
                </span>
                {title}
            </h3>
            <p style="margin: 4px 0; color: #666; font-size: 14px;">
                <strong>{company}</strong> • {location}
            </p>
            <p style="margin: 8px 0; color: #888; font-size: 13px;">
                {h1b_emoji} {target_indicator}
            </p>
            <p style="margin: 12px 0; font-size: 14px; line-height: 1.5;">
                {description}...
            </p>
            <p style="margin: 8px 0; color: #555; font-size: 13px;">
                <strong>Tech Stack:</strong> {tech_stack}
            </p>
            <p style="margin: 12px 0;">
                <a href="{url}" style="background: #2196F3; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">
                    View Job
                </a>
            </p>
        </div>
        """
        
        job_rows.append(job_html)
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }}
        </style>
    </head>
    <body style="margin: 0; padding: 20px; background: #f5f5f5;">
        <div style="max-width: 800px; margin: 0 auto; background: white; padding: 24px; border-radius: 8px;">
            <h1 style="margin: 0 0 8px 0; color: #333;">Job Digest</h1>
            <p style="margin: 0 0 24px 0; color: #666;">
                {len(jobs)} high-scoring matches • {datetime.now().strftime('%B %d, %Y')}
            </p>
            
            {''.join(job_rows)}
            
            <hr style="margin: 32px 0; border: none; border-top: 1px solid #ddd;">
            
            <p style="color: #888; font-size: 13px; text-align: center;">
                Automated Job Hunter Pipeline • Generated {datetime.now().strftime('%I:%M %p')}
            </p>
        </div>
    </body>
    </html>
    """
    
    return html


def _build_completion_html(jobs: List[Dict]) -> str:
    """Build HTML for Step 2 completion email."""
    
    job_rows = []
    
    for job in jobs:
        title = job.get('title', 'Unknown Title')
        company = job.get('company', 'Unknown Company')
        doc_url = job.get('doc_url', '#')
        email_doc_url = job.get('email_doc_url', '#')
        resume_pdf_url = job.get('resume_pdf_url', '#')
        
        job_html = f"""
        <div style="border: 1px solid #ddd; padding: 16px; margin-bottom: 16px; border-radius: 8px;">
            <h3 style="margin: 0 0 8px 0; color: #333;">{title}</h3>
            <p style="margin: 4px 0; color: #666;">{company}</p>
            <p style="margin: 12px 0;">
                <a href="{resume_pdf_url}" style="background: #FF5722; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-right: 8px; display: inline-block;">
                    Resume PDF
                </a>
                <a href="{doc_url}" style="background: #4CAF50; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-right: 8px; display: inline-block;">
                    Resume Doc
                </a>
                <a href="{email_doc_url}" style="background: #2196F3; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">
                    Email Doc
                </a>
            </p>
        </div>
        """
        
        job_rows.append(job_html)
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }}
        </style>
    </head>
    <body style="margin: 0; padding: 20px; background: #f5f5f5;">
        <div style="max-width: 800px; margin: 0 auto; background: white; padding: 24px; border-radius: 8px;">
            <h1 style="margin: 0 0 8px 0; color: #333;">Tailored Resumes Ready</h1>
            <p style="margin: 0 0 24px 0; color: #666;">
                {len(jobs)} jobs processed • {datetime.now().strftime('%B %d, %Y')}
            </p>
            
            {''.join(job_rows)}
            
            <hr style="margin: 32px 0; border: none; border-top: 1px solid #ddd;">
            
            <p style="color: #888; font-size: 13px; text-align: center;">
                Automated Job Hunter Pipeline • Generated {datetime.now().strftime('%I:%M %p')}
            </p>
        </div>
    </body>
    </html>
    """
    
    return html
