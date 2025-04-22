"""Example of batch processing multiple URLs with AgnostiScrape.ai"""

import asyncio
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file (for GEMINI_API_KEY)
load_dotenv()

# Import the main class
from agnostiscrape import WebsiteScreenshotVLM
from agnostiscrape.config import ScreenshotConfig, StorageConfig, VLMConfig

async def main():
    """Example of batch processing multiple URLs."""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create instance with custom configuration
    scraper = WebsiteScreenshotVLM(
        screenshot_config=ScreenshotConfig(
            headless=True,
            browser_types=["chromium", "firefox"],
            timeout_seconds=60
        ),
        storage_config=StorageConfig(
            output_dir="./batch_results",
            cleanup_screenshots=False
        ),
        max_concurrent=2, # Process 2 URLs concurrently
        log_level=logging.INFO
    )
    
    # List of URLs to process
    urls = [
        "https://www.amazon.com/Apple-MacBook-16-inch-10%E2%80%91core-16%E2%80%91core/dp/B0CM5JS1GQ/",
        "https://www.bestbuy.com/site/apple-macbook-pro-16-liquid-retina-xdr-display-apple-m3-pro-chip-with-12-core-cpu-and-18-core-gpu-18gb-memory-512gb-ssd-space-black/6534641.p",
        "https://www.bhphotovideo.com/c/product/1773230-REG/apple_mrx33ll_a_16_macbook_pro_with.html"
    ]
    
    try:
        # Process multiple URLs
        results = await scraper.process_batch(urls, "product")
        
        # Display results
        print("\nBatch Processing Results:")
        for url, result in results.items():
            print(f"\nURL: {url}")
            # Show just product name and price from each result
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                try:
                    print(f"Product: {result.get('product_name', 'N/A')}")
                    print(f"Price: {result.get('price', 'N/A')}")
                except:
                    print("Error parsing result")
        
        # Save full results to a file
        with open("batch_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results saved to batch_results.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 