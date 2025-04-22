"""Example of using AgnostiScrape.ai with a custom prompt template"""

import asyncio
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file (for GEMINI_API_KEY)
load_dotenv()

# Import the main class and configs
from agnostiscrape import WebsiteScreenshotVLM
from agnostiscrape.config import ScreenshotConfig, VLMConfig, StorageConfig

# Custom prompt for scraping real estate listings
REAL_ESTATE_PROMPT = """Analyze this real estate listing page screenshot and extract the following information in valid JSON format:
{
    "property_type": "Type of property (e.g., House, Apartment, Condo)",
    "address": "Full address of the property",
    "price": "Listed price with currency",
    "bedrooms": "Number of bedrooms (numeric value only)",
    "bathrooms": "Number of bathrooms (numeric value only)",
    "square_footage": "Square footage of the property (numeric value only)",
    "year_built": "Year the property was built (if available, otherwise null)",
    "description": "Brief description of the property",
    "amenities": ["List of key amenities"],
    "agent_name": "Real estate agent name (if available, otherwise null)",
    "listing_date": "When the property was listed (if available, otherwise null)"
}
Make sure to return ONLY valid JSON with no additional text."""

async def main():
    """Example of using a custom prompt template."""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create custom VLM config with the real estate prompt
    vlm_config = VLMConfig(
        prompt_templates={
            "product": VLMConfig().prompt_templates["product"],  # Keep default product prompt
            "article": VLMConfig().prompt_templates["article"],  # Keep default article prompt
            "real_estate": REAL_ESTATE_PROMPT  # Add new prompt type
        },
        default_data_type="real_estate"  # Set as default
    )
    
    # Create scraper with custom configuration
    scraper = WebsiteScreenshotVLM(
        screenshot_config=ScreenshotConfig(
            headless=True,
            browser_types=["chromium"],
            timeout_seconds=60
        ),
        vlm_config=vlm_config,
        storage_config=StorageConfig(
            output_dir="./real_estate_results",
            cleanup_screenshots=False
        ),
        max_concurrent=1,
        log_level=logging.INFO
    )
    
    # URL to process - example real estate listing
    url = "https://www.zillow.com/homedetails/2636-Stockbridge-Dr-Oakland-CA-94611/24773530_zpid/"
    
    try:
        # Process the real estate listing
        result = await scraper.process_url(url, "real_estate")
        
        # Display the extracted data
        print("\nExtracted Real Estate Data:")
        print(f"Property Type: {result.get('property_type', 'N/A')}")
        print(f"Address: {result.get('address', 'N/A')}")
        print(f"Price: {result.get('price', 'N/A')}")
        print(f"Bedrooms: {result.get('bedrooms', 'N/A')}")
        print(f"Bathrooms: {result.get('bathrooms', 'N/A')}")
        print(f"Square Footage: {result.get('square_footage', 'N/A')}")
        
        # Save full results to a file
        with open("real_estate_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nFull results saved to real_estate_result.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 