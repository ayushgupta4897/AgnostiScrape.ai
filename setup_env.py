#!/usr/bin/env python3
"""
Environment setup script for AgnostiScrape.ai

This script helps users set up their environment for using AgnostiScrape.ai:
1. Checks for required dependencies
2. Installs Playwright browsers
3. Verifies the Gemini API key is set
4. Creates necessary directories
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from dotenv import load_dotenv

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def print_step(message):
    """Print a step message"""
    print(f"\n➤ {message}")

def check_python_version():
    """Check that Python is 3.8 or higher"""
    print_step("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ is required, but you have {sys.version.split()[0]}")
        print("Please upgrade Python and try again.")
        sys.exit(1)
    else:
        print(f"✅ Python version {sys.version.split()[0]} (OK)")

def install_dependencies(include_streamlit=False):
    """Install required Python packages"""
    print_step("Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Core dependencies installed successfully")
        
        if include_streamlit:
            print_step("Installing Streamlit UI dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "streamlit_requirements.txt"])
            print("✅ Streamlit UI dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Please run: pip install -e .")
        sys.exit(1)

def install_playwright_browsers():
    """Install Playwright browsers"""
    print_step("Installing Playwright browsers...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium", "firefox"])
        print("✅ Playwright browsers installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Playwright browsers")
        print("Please run: playwright install chromium firefox")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Playwright command not found")
        print("Please make sure the playwright package is installed")
        sys.exit(1)

def check_api_key():
    """Check if the Gemini API key is set"""
    print_step("Checking Gemini API key...")
    
    # Try to load from .env file
    load_dotenv()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        
        # If .env file doesn't exist, create one
        env_file = Path(".env")
        if not env_file.exists():
            # Ask user for API key
            print("\nPlease enter your Gemini API key (or press Enter to skip):")
            print("You can get one from: https://aistudio.google.com/app/apikey")
            api_key = input("> ").strip()
            
            if api_key:
                with open(env_file, "w") as f:
                    f.write(f"GEMINI_API_KEY={api_key}\n")
                print("✅ API key saved to .env file")
            else:
                print("⚠️ No API key provided. You'll need to set it later.")
                with open(env_file, "w") as f:
                    f.write("# Get your API key from: https://aistudio.google.com/app/apikey\n")
                    f.write("GEMINI_API_KEY=your_api_key_here\n")
                print("A template .env file has been created.")
    else:
        print("✅ GEMINI_API_KEY is set")

def create_directories():
    """Create necessary directories"""
    print_step("Creating output directories...")
    
    directories = ["screenshots", "batch_results", "real_estate_results", "custom_vlm_results"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Output directories created")

def main():
    """Main setup function"""
    print_header("AgnostiScrape.ai Environment Setup")
    
    print("This script will set up your environment for using AgnostiScrape.ai.")
    print("It will check dependencies, install browsers, and verify your API key.")
    
    # Ask if user wants to install Streamlit UI
    include_streamlit = input("\nDo you want to install the Streamlit UI? (y/n): ").lower().startswith('y')
    
    check_python_version()
    install_dependencies(include_streamlit)
    install_playwright_browsers()
    check_api_key()
    create_directories()
    
    print_header("Setup Complete!")
    print("You're now ready to use AgnostiScrape.ai.")
    
    if include_streamlit:
        print("\nTo run the Streamlit UI:")
        print("  streamlit run streamlit_app.py")
    else:
        print("\nTo try a simple example:")
        print("  python examples/simple_scrape.py")
    
if __name__ == "__main__":
    main()