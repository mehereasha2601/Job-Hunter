#!/usr/bin/env python3
"""
Quick test to verify API keys are working.
Run this before running the full test harness.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_groq():
    """Test Groq API key."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not set")
        return False
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'hello' if you can hear me."}],
            temperature=0.3,
            max_tokens=50
        )
        print(f"✓ Groq API working: {response.choices[0].message.content[:50]}")
        return True
    except Exception as e:
        print(f"❌ Groq API failed: {str(e)}")
        return False


def test_gemini():
    """Test Gemini API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Say 'hello' if you can hear me.")
        print(f"✓ Gemini API working: {response.text[:50]}")
        return True
    except Exception as e:
        print(f"❌ Gemini API failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("API Key Verification")
    print("="*60)
    print()
    
    groq_ok = test_groq()
    print()
    gemini_ok = test_gemini()
    print()
    
    if groq_ok and gemini_ok:
        print("✓ All API keys working! You can now run the test harness:")
        print("  python tests/test_harness.py")
        sys.exit(0)
    else:
        print("⚠️  Some API keys are missing or invalid.")
        print("   1. Copy .env.example to .env")
        print("   2. Add your API keys")
        print("   3. Run this script again")
        sys.exit(1)
