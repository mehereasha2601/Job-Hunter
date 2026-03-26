"""
Rate limit monitor for Apify and GitHub Actions.
Section 16 of spec.md.
"""

import requests
from typing import Dict
from src.config import Config


class RateLimitMonitor:
    """Monitor rate limits for external services."""
    
    def __init__(self):
        """Initialize rate limit monitor."""
        pass
    
    def check_apify(self) -> Dict:
        """
        Check Apify credit balance.
        
        Returns:
            {
                'remaining': float,
                'total': float,
                'percentage': float,
                'warning': bool
            }
        """
        if not Config.APIFY_TOKEN:
            return {
                'remaining': 0,
                'total': 0,
                'percentage': 0,
                'warning': True,
                'error': 'APIFY_TOKEN not configured'
            }
        
        try:
            url = f"https://api.apify.com/v2/users/me?token={Config.APIFY_TOKEN}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return {
                    'remaining': 0,
                    'total': 0,
                    'percentage': 0,
                    'warning': True,
                    'error': f'API error: {response.status_code}'
                }
            
            data = response.json()['data']
            
            # Extract credits
            total_credits = data.get('usage', {}).get('freeMonthlyLimit', 0)
            used_credits = data.get('usage', {}).get('monthlyUsage', {}).get('USD', 0)
            remaining = total_credits - used_credits
            
            percentage = (remaining / total_credits * 100) if total_credits > 0 else 0
            warning = percentage < (Config.RATE_LIMIT_WARNING_THRESHOLD * 100)
            
            return {
                'remaining': remaining,
                'total': total_credits,
                'percentage': percentage,
                'warning': warning
            }
        
        except Exception as e:
            return {
                'remaining': 0,
                'total': 0,
                'percentage': 0,
                'warning': True,
                'error': str(e)
            }
    
    def check_github_actions(self) -> Dict:
        """
        Check GitHub Actions minutes remaining.
        
        Returns:
            {
                'remaining': int,
                'total': int,
                'percentage': float,
                'warning': bool
            }
        """
        if not Config.GH_PAT:
            return {
                'remaining': 0,
                'total': 0,
                'percentage': 0,
                'warning': True,
                'error': 'GH_PAT not configured'
            }
        
        try:
            # Get billing info for authenticated user
            url = 'https://api.github.com/user'
            headers = {
                'Authorization': f'Bearer {Config.GH_PAT}',
                'Accept': 'application/vnd.github+json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    'remaining': 0,
                    'total': 0,
                    'percentage': 0,
                    'warning': True,
                    'error': f'API error: {response.status_code}'
                }
            
            user_data = response.json()
            username = user_data['login']
            
            # Get billing/actions
            billing_url = f'https://api.github.com/users/{username}/settings/billing/actions'
            billing_response = requests.get(billing_url, headers=headers, timeout=10)
            
            if billing_response.status_code != 200:
                # May not have access to billing info
                return {
                    'remaining': -1,
                    'total': -1,
                    'percentage': 100,
                    'warning': False,
                    'info': 'Billing info not accessible'
                }
            
            billing_data = billing_response.json()
            
            total_minutes = billing_data.get('included_minutes', 0)
            used_minutes = billing_data.get('total_minutes_used', 0)
            remaining = total_minutes - used_minutes
            
            percentage = (remaining / total_minutes * 100) if total_minutes > 0 else 0
            warning = percentage < (Config.RATE_LIMIT_WARNING_THRESHOLD * 100)
            
            return {
                'remaining': remaining,
                'total': total_minutes,
                'percentage': percentage,
                'warning': warning
            }
        
        except Exception as e:
            return {
                'remaining': 0,
                'total': 0,
                'percentage': 0,
                'warning': True,
                'error': str(e)
            }
    
    def check_groq(self) -> Dict:
        """
        Check Groq rate limits (if API provides endpoint).
        For now, returns placeholder.
        """
        # Groq doesn't expose rate limit info via API
        return {
            'info': 'Groq limits: 30 RPM, 14400 RPD, 100K tokens/day (tracked client-side)',
            'warning': False
        }
    
    def check_gemini(self) -> Dict:
        """
        Check Gemini rate limits.
        Gemini Flash has generous free tier, unlikely to hit limits.
        """
        return {
            'info': 'Gemini Flash 2.0: 1500 RPD free tier',
            'warning': False
        }
    
    def get_status(self) -> Dict:
        """
        Get comprehensive rate limit status for all services.
        
        Returns:
            Dict with status for each service
        """
        return {
            'apify': self.check_apify(),
            'github_actions': self.check_github_actions(),
            'groq': self.check_groq(),
            'gemini': self.check_gemini(),
            'any_warnings': self.check_apify()['warning'] or self.check_github_actions()['warning']
        }
