"""Example showing how to use AgnostiScrape.ai with a different VLM provider"""

import asyncio
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the main class and configs
from agnostiscrape import WebsiteScreenshotVLM
from agnostiscrape.config import ScreenshotConfig, VLMConfig, StorageConfig

# Replace this with actual implementation of an alternative VLM client
async def custom_vlm_processor(image_path: str, prompt: str) -> str:
    """
    Example of a custom VLM client that uses an alternative provider.
    
    In a real implementation, this would call your preferred VLM API.
    This is just a placeholder for demonstration.
    
    Args:
        image_path: Path to the screenshot image
        prompt: Prompt to send to the VLM
        
    Returns:
        JSON response string from the VLM
    """
    try:
        # In a real implementation, you would:
        # 1. Load the image
        # 2. Call your VLM API (OpenAI, Anthropic, etc.)
        # 3. Return the response
        
        # This is just a placeholder that returns a mock response
        print(f"Processing image {image_path} with prompt: {prompt[:50]}...")
        
        # Mock response - in reality this would come from your VLM API
        mock_response = """
        {
            "product_name": "Example Product",
            "price": "$99.99",
            "rating": "4.5 stars",
            "num_reviews": "42",
            "description": "This is an example product description",
            "key_features": ["Feature 1", "Feature 2", "Feature 3"],
            "availability": "In stock",
            "seller": "Example Seller"
        }
        """
        
        return mock_response
        
    except Exception as e:
        logging.error(f"Error in custom VLM processing: {e}")
        return f"{{\"error\": \"{str(e)}\"}}"

class CustomVLMScraper(WebsiteScreenshotVLM):
    """Custom scraper class that overrides the VLM processing method"""
    
    async def extract_data_from_image(self, image_path: str, prompt: str) -> dict:
        """
        Override the default VLM extraction with our custom implementation.
        
        Args:
            image_path: Path to the image
            prompt: Prompt to send to the VLM
            
        Returns:
            Extracted data as a dictionary
        """
        try:
            # Use our custom VLM processor instead of the default Gemini one
            result = await custom_vlm_processor(image_path, prompt)
            
            # Parse JSON from result
            json_str = result.strip()
            if not json_str.startswith('{'):
                start = json_str.find('{')
                end = json_str.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = json_str[start:end]
            
            # Parse JSON
            try:
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError:
                self.logger.error(f"Failed to parse JSON from VLM response: {json_str}")
                return {"error": "JSON parsing error", "raw_response": json_str}
            
        except Exception as e:
            self.logger.error(f"Error extracting data from image: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {"error": str(e)}

async def main():
    """Example of using a custom VLM implementation."""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create scraper with custom VLM implementation
    scraper = CustomVLMScraper(
        screenshot_config=ScreenshotConfig(
            headless=True,
            browser_types=["chromium"],
            timeout_seconds=60
        ),
        storage_config=StorageConfig(
            output_dir="./custom_vlm_results",
            cleanup_screenshots=False
        ),
        max_concurrent=1,
        log_level=logging.INFO
    )
    
    # URL to process
    url = "https://www.example.com/product"
    
    try:
        # Process the URL
        print(f"Processing URL: {url}")
        result = await scraper.process_url(url, "product")
        
        # Display the extracted data
        print("\nExtracted Data (via custom VLM):")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 