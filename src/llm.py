"""
LLM client with Groq (primary) and Gemini (fallback) support.
Handles rate limiting with automatic fallback between providers.
"""

import os
import json
from typing import Optional, Dict, Any
from groq import Groq
import google.generativeai as genai


class LLMClient:
    """LLM client with automatic fallback between Groq and Gemini."""
    
    def __init__(self):
        self.groq_client = None
        self.gemini_model = None
        
        # Initialize Groq
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.groq_client = Groq(api_key=groq_key)
        
        # Initialize Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            # Use models/gemini-2.5-flash (need models/ prefix)
            self.gemini_model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        prefer_groq: bool = True
    ) -> Dict[str, Any]:
        """
        Call LLM with automatic fallback.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature setting (default 0.3)
            max_tokens: Max tokens to generate
            prefer_groq: Try Groq first if True, Gemini first if False
        
        Returns:
            Dict with keys: 'text', 'provider', 'success', 'error'
        """
        providers = ['groq', 'gemini'] if prefer_groq else ['gemini', 'groq']
        
        for provider in providers:
            try:
                if provider == 'groq':
                    result = self._call_groq(prompt, system_prompt, temperature, max_tokens)
                else:
                    result = self._call_gemini(prompt, system_prompt, temperature, max_tokens)
                
                if result['success']:
                    return result
            except Exception as e:
                print(f"[{provider}] failed: {str(e)}")
                continue
        
        return {
            'text': '',
            'provider': 'none',
            'success': False,
            'error': 'All LLM providers failed'
        }
    
    def _call_groq(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call Groq API with Llama 3.3 70B."""
        if not self.groq_client:
            return {
                'text': '',
                'provider': 'groq',
                'success': False,
                'error': 'Groq client not initialized (API key missing)'
            }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            'text': response.choices[0].message.content,
            'provider': 'groq',
            'success': True,
            'error': None
        }
    
    def _call_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call Gemini API with Flash 2.0."""
        if not self.gemini_model:
            return {
                'text': '',
                'provider': 'gemini',
                'success': False,
                'error': 'Gemini client not initialized (API key missing)'
            }
        
        # Combine system prompt and user prompt for Gemini
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        generation_config = {
            'temperature': temperature,
            'max_output_tokens': max_tokens,
        }
        
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return {
            'text': response.text,
            'provider': 'gemini',
            'success': True,
            'error': None
        }
