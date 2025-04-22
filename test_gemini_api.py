#!/usr/bin/env python3
"""
Test script for Gemini API key

This script tests if your GEMINI_API_KEY environment variable is set correctly
and can connect to the Gemini API successfully.
"""

import os
import sys
from dotenv import load_dotenv
from google import genai

def main():
    """Test Gemini API key"""
    print("Testing Gemini API connection...")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY is not set in environment or .env file")
        print("\nPlease set the GEMINI_API_KEY environment variable:")
        print("  1. Create a .env file in the root directory of the project")
        print("  2. Add the line GEMINI_API_KEY=your_api_key_here with your actual API key")
        print("  3. Run this script again")
        sys.exit(1)
    
    print("✅ GEMINI_API_KEY is set")
    
    # Try to initialize the Gemini client
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Gemini client initialized successfully")
    except Exception as e:
        print(f"❌ ERROR initializing Gemini client: {e}")
        sys.exit(1)
    
    # Try to list available models
    try:
        models = [model.name for model in client.list_models() if "gemini" in model.name.lower()]
        print(f"✅ Successfully connected to Gemini API")
        print(f"Available models: {', '.join(models)}")
    except Exception as e:
        print(f"❌ ERROR connecting to Gemini API: {e}")
        sys.exit(1)
    
    print("\n=== Test Completed Successfully ===")
    print("Your Gemini API key is working correctly!")
    print("You can now use AgnostiScrape.ai to extract data from websites.")
    
if __name__ == "__main__":
    main() 