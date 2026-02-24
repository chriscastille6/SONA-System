#!/usr/bin/env python3
"""
Test Gemini API connection.

Run from project root with .env loaded:
  python scripts/test_gemini_connection.py

Or with explicit key:
  GEMINI_API_KEY=your-key python scripts/test_gemini_connection.py
"""
import os
import sys
from pathlib import Path

# Load .env from project root
project_root = Path(__file__).resolve().parent.parent
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value and key not in os.environ:
                    os.environ[key] = value

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not set. Add it to .env or export it.")
    sys.exit(1)

try:
    from google import genai
except ImportError:
    print("ERROR: google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

def main():
    print("Testing Gemini API connection...")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly: Hello World",
    )
    text = response.text if hasattr(response, "text") else str(response)
    print(f"Response: {text}")
    if "Hello" in text or "hello" in text.lower():
        print("SUCCESS: Gemini connection working!")
    else:
        print("WARNING: Got response but unexpected content.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
