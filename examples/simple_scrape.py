"""Simple example of using AgnostiScrape.ai to extract product data"""

import asyncio
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file (for GEMINI_API_KEY)
load_dotenv()

# Import the main class
from agnostiscrape import WebsiteScreenshotVLM
from agnostiscrape.config import ScreenshotConfig, StorageConfig

async def main():
    """Example usage of WebsiteScreenshotVLM."""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create instance with custom configuration
    scraper = WebsiteScreenshotVLM(
        screenshot_config=ScreenshotConfig(
            headless=True,
            browser_types=["chromium"],
            timeout_seconds=60
        ),
        storage_config=StorageConfig(
            output_dir="./screenshot_results",
            cleanup_screenshots=False
        ),
        max_concurrent=1,
        log_level=logging.INFO
    )
    
    # URL to process
    url = "https://www.amazon.com/Apple-MacBook-16-inch-10%E2%80%91core-16%E2%80%91core/dp/B0CM5JS1GQ/"
    
    try:
        # Process single URL
        result = await scraper.process_url(url, "product")
        
        # Display result
        print("\nExtracted Data:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())