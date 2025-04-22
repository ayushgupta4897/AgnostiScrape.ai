from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response
from typing import List, Dict, Any, Optional, Union, Tuple, Set, Callable, TypeVar, Generic, Literal
import time
import random
import json
import asyncio
import sys
import os
import logging
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("screenshot-vlm")

# Type definitions
T = TypeVar('T')
BrowserType = Literal["chromium", "firefox", "webkit"]
WaitUntilState = Literal["load", "domcontentloaded", "networkidle"]

@dataclass
class ScreenshotConfig:
    """Configuration for screenshot capture functionality"""
    headless: bool = True
    browser_types: List[BrowserType] = field(default_factory=lambda: ["chromium", "firefox"])
    viewport_width: int = 1920
    viewport_height: int = 1080
    device_scale_factor: float = 2.0
    timeout_seconds: int = 45
    wait_until: WaitUntilState = "domcontentloaded"
    locale: str = "en-US"
    timezone_id: str = "UTC"
    full_page: bool = True
    post_load_delay_ms: int = 3000
    scroll_percent: float = 0.6
    browser_args: List[str] = field(default_factory=lambda: [
        "--disable-blink-features=AutomationControlled",
        "--disable-http2", 
        "--no-sandbox"
    ])
    max_retries: int = 2
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    extra_headers: Dict[str, str] = field(default_factory=lambda: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "sec-ch-ua": '"Chromium";v="122", "Google Chrome";v="122", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    })

@dataclass
class VLMConfig:
    """Configuration for VLM processing"""
    prompt_templates: Dict[str, str] = field(default_factory=lambda: {
        "product": """Analyze this product page screenshot and extract the following information in valid JSON format:
{
    "product_name": "Full product name",
    "price": "Current price with currency",
    "rating": "Average rating (if available, otherwise null)",
    "num_reviews": "Number of reviews (if available, otherwise null)",
    "description": "Short product description",
    "key_features": ["List of key features"],
    "availability": "In stock or not",
    "seller": "Seller name (if available, otherwise null)"
}
Make sure to return ONLY valid JSON with no additional text.""",
        
        "article": """Analyze this article page screenshot and extract the following information in valid JSON format:
{
    "title": "Article title",
    "author": "Author name (if available, otherwise null)",
    "date_published": "Publication date (if available, otherwise null)",
    "summary": "A brief summary of the article (2-3 sentences)",
    "main_topics": ["List of main topics covered"],
    "source": "Name of the publication or website"
}
Make sure to return ONLY valid JSON with no additional text."""
    })
    default_data_type: str = "product"
    
@dataclass
class StorageConfig:
    """Configuration for storage and file management"""
    output_dir: str = "./screenshots"
    cleanup_screenshots: bool = False
    keep_days: int = 7
    file_prefix: str = "screenshot_"
    data_file_prefix: str = "data_"
    

class WebsiteScreenshotVLM:
    """
    A production-ready class for capturing website screenshots and processing them with VLM.
    
    This class handles:
    - Capturing screenshots of websites using Playwright
    - Processing screenshots with VLM to extract structured data
    - Managing storage and cleanup of files
    - Configurable concurrency and retries
    - Detailed logging and error handling
    """
    
    def __init__(
        self, 
        screenshot_config: Optional[ScreenshotConfig] = None,
        vlm_config: Optional[VLMConfig] = None,
        storage_config: Optional[StorageConfig] = None,
        max_concurrent: int = 3,
        log_level: int = logging.INFO
    ):
        """
        Initialize the WebsiteScreenshotVLM instance with the given configurations.
        
        Args:
            screenshot_config: Configuration for screenshot capture
            vlm_config: Configuration for VLM processing
            storage_config: Configuration for storage management
            max_concurrent: Maximum number of concurrent operations
            log_level: Logging level
        """
        self.screenshot_config = screenshot_config or ScreenshotConfig()
        self.vlm_config = vlm_config or VLMConfig()
        self.storage_config = storage_config or StorageConfig()
        self.max_concurrent = max_concurrent
        
        # Set up logging
        self.logger = logger
        self.logger.setLevel(log_level)
        
        # Create semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create output directory
        os.makedirs(self.storage_config.output_dir, exist_ok=True)
        
    async def initialize_browser(self, browser_type_name: BrowserType) -> Tuple[Browser, BrowserContext]:
        """
        Initialize a browser and context with the given configuration.
        
        Args:
            browser_type_name: Type of browser to launch
            
        Returns:
            Tuple of browser and browser context
        """
        async with async_playwright() as playwright:
            # Get browser type object
            browser_type = getattr(playwright, browser_type_name)
            
            # Launch browser with configuration
            browser = await browser_type.launch(
                headless=self.screenshot_config.headless,
                args=self.screenshot_config.browser_args
            )
            
            # Create context with configuration
            context = await browser.new_context(
                viewport={
                    "width": self.screenshot_config.viewport_width, 
                    "height": self.screenshot_config.viewport_height
                },
                user_agent=self.screenshot_config.user_agent,
                locale=self.screenshot_config.locale,
                timezone_id=self.screenshot_config.timezone_id,
                device_scale_factor=self.screenshot_config.device_scale_factor
            )
            
            # Add script to mask automation
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                window.chrome = { runtime: {} };
            """)
            
            return browser, context
    
    async def capture_screenshot(self, url: str) -> Optional[bytes]:
        """
        Capture a screenshot of the given URL.
        
        Args:
            url: URL to capture
            
        Returns:
            Screenshot bytes if successful, None otherwise
        """
        async with self.semaphore:
            for retry in range(self.screenshot_config.max_retries + 1):
                if retry > 0:
                    self.logger.info(f"Retry {retry}/{self.screenshot_config.max_retries} for {url}")
                
                # Try each browser type until successful
                for browser_type in self.screenshot_config.browser_types:
                    self.logger.info(f"Trying {browser_type} for {url}")
                    browser = None
                    
                    try:
                        async with async_playwright() as p:
                            # Get browser type object
                            browser_type_obj = getattr(p, browser_type)
                            
                            # Launch browser with configuration
                            browser = await browser_type_obj.launch(
                                headless=self.screenshot_config.headless,
                                args=self.screenshot_config.browser_args
                            )
                            
                            # Create context with configuration
                            context = await browser.new_context(
                                viewport={
                                    "width": self.screenshot_config.viewport_width, 
                                    "height": self.screenshot_config.viewport_height
                                },
                                user_agent=self.screenshot_config.user_agent,
                                locale=self.screenshot_config.locale,
                                timezone_id=self.screenshot_config.timezone_id,
                                device_scale_factor=self.screenshot_config.device_scale_factor
                            )
                            
                            # Add script to mask automation
                            await context.add_init_script("""
                                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                                window.chrome = { runtime: {} };
                            """)
                            
                            # Create page with headers
                            page = await context.new_page()
                            await page.set_extra_http_headers(self.screenshot_config.extra_headers)
                            
                            # Navigate to URL
                            self.logger.info(f"Navigating to {url}")
                            response = await page.goto(
                                url, 
                                wait_until=self.screenshot_config.wait_until, 
                                timeout=self.screenshot_config.timeout_seconds * 1000
                            )
                            
                            # Check response status
                            if not response or response.status >= 400:
                                self.logger.warning(f"Failed to load {url}: {response.status if response else 'No response'}")
                                await browser.close()
                                continue
                            
                            # Wait for additional content to load
                            await page.wait_for_timeout(self.screenshot_config.post_load_delay_ms)
                            
                            # Scroll to simulate user behavior
                            await page.evaluate(f"""
                                window.scrollTo({{
                                    top: document.body.scrollHeight * {self.screenshot_config.scroll_percent},
                                    behavior: 'smooth'
                                }});
                            """)
                            await page.wait_for_timeout(1000)
                            
                            # Scroll back to top
                            await page.evaluate("window.scrollTo(0, 0);")
                            await page.wait_for_timeout(500)
                            
                            # Take screenshot
                            self.logger.info(f"Taking screenshot of {url}")
                            screenshot = await page.screenshot(full_page=self.screenshot_config.full_page)
                            
                            # Close browser
                            await browser.close()
                            
                            return screenshot
                    
                    except Exception as e:
                        self.logger.error(f"Error capturing {url} with {browser_type}: {e}")
                        if browser:
                            try:
                                await browser.close()
                            except:
                                pass
            
            self.logger.error(f"Failed to capture {url} after {self.screenshot_config.max_retries + 1} attempts")
            return None
    
    async def extract_data_from_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Extract structured data from an image using VLM.
        
        Args:
            image_path: Path to the image
            prompt: Prompt to send to the VLM
            
        Returns:
            Extracted data as a dictionary
        """
        async with self.semaphore:
            try:
                # Import VLM client
                sys.path.append(".")
                from clients.gemini import query_image_path
                
                # Query VLM
                self.logger.info(f"Querying VLM with image {image_path}")
                result = await query_image_path(image_path, prompt)
                
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
    
    def get_prompt(self, data_type: str) -> str:
        """
        Get the prompt template for the given data type.
        
        Args:
            data_type: Type of data to extract
            
        Returns:
            Prompt template string
        """
        return self.vlm_config.prompt_templates.get(
            data_type, 
            self.vlm_config.prompt_templates[self.vlm_config.default_data_type]
        )
    
    def generate_file_paths(self, url: str) -> Tuple[str, str]:
        """
        Generate file paths for screenshot and data files.
        
        Args:
            url: URL to generate paths for
            
        Returns:
            Tuple of (screenshot_path, data_path)
        """
        # Create hash of URL for filename
        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        
        # Generate paths
        screenshot_path = os.path.join(
            self.storage_config.output_dir, 
            f"{self.storage_config.file_prefix}{url_hash}.png"
        )
        data_path = os.path.join(
            self.storage_config.output_dir, 
            f"{self.storage_config.data_file_prefix}{url_hash}.json"
        )
        
        return screenshot_path, data_path
    
    async def cleanup_old_files(self) -> None:
        """
        Clean up old screenshot and data files.
        """
        if not self.storage_config.cleanup_screenshots:
            return
        
        try:
            now = time.time()
            max_age = self.storage_config.keep_days * 24 * 60 * 60
            
            for filename in os.listdir(self.storage_config.output_dir):
                if filename.startswith(self.storage_config.file_prefix) or \
                   filename.startswith(self.storage_config.data_file_prefix):
                    file_path = os.path.join(self.storage_config.output_dir, filename)
                    
                    # Get file age
                    file_age = now - os.path.getmtime(file_path)
                    
                    # Remove if too old
                    if file_age > max_age:
                        self.logger.info(f"Removing old file: {file_path}")
                        os.remove(file_path)
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old files: {e}")
    
    async def process_url(self, url: str, data_type: str = None) -> Dict[str, Any]:
        """
        Process a URL: capture screenshot and extract data.
        
        Args:
            url: URL to process
            data_type: Type of data to extract, defaults to config default
            
        Returns:
            Extracted data as a dictionary
        """
        # Use default data type if not specified
        data_type = data_type or self.vlm_config.default_data_type
        
        # Get prompt
        prompt = self.get_prompt(data_type)
        
        # Generate file paths
        screenshot_path, data_path = self.generate_file_paths(url)
        
        # Capture screenshot
        screenshot = await self.capture_screenshot(url)
        
        if screenshot:
            # Save screenshot
            with open(screenshot_path, "wb") as f:
                f.write(screenshot)
            self.logger.info(f"Screenshot saved to {screenshot_path}")
            
            # Extract data
            data = await self.extract_data_from_image(screenshot_path, prompt)
            
            # Add metadata
            data["_metadata"] = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "data_type": data_type
            }
            
            # Save data
            with open(data_path, "w") as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Data saved to {data_path}")
            
            # Clean up screenshot if needed
            if self.storage_config.cleanup_screenshots:
                try:
                    os.remove(screenshot_path)
                    self.logger.info(f"Cleaned up screenshot: {screenshot_path}")
                except Exception as e:
                    self.logger.error(f"Error cleaning up screenshot: {e}")
            
            return data
        else:
            error_data = {
                "error": "Failed to capture screenshot",
                "_metadata": {
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "data_type": data_type
                }
            }
            
            # Save error data
            with open(data_path, "w") as f:
                json.dump(error_data, f, indent=2)
            
            return error_data
    
    async def process_batch(self, urls: List[str], data_type: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Process a batch of URLs concurrently.
        
        Args:
            urls: List of URLs to process
            data_type: Type of data to extract, defaults to config default
            
        Returns:
            Dictionary mapping URLs to their extracted data
        """
        # Clean up old files
        await self.cleanup_old_files()
        
        # Process URLs concurrently
        tasks = [self.process_url(url, data_type) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results to URLs
        result_dict = {}
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                self.logger.error(f"Error processing {url}: {result}")
                result_dict[url] = {"error": str(result)}
            else:
                result_dict[url] = result
        
        return result_dict

async def main():
    """
    Example usage of WebsiteScreenshotVLM.
    """
    # Create instance with custom configuration
    scraper = WebsiteScreenshotVLM(
        screenshot_config=ScreenshotConfig(
            headless=True,
            browser_types=["chromium", "firefox"],
            timeout_seconds=60
        ),
        storage_config=StorageConfig(
            output_dir="./screenshot_results",
            cleanup_screenshots=False
        ),
        max_concurrent=2,
        log_level=logging.INFO
    )
    
    # URLs to process
    urls = [
        "https://www.nykaa.com/sol-de-janeiro-brazilian-crush-body-hair-mist/p/2722203?productId=2722203&pps=1&skuId=2722198"
    ]
    try:
        # Process single URL
        result = await scraper.process_url(urls[0], "product")
        
        # Display result
        print("\nExtracted Data:")
        print(json.dumps(result, indent=2))
        
        # Example of batch processing
        # batch_results = await scraper.process_batch(urls, "product")
        # print("\nBatch Results:")
        # print(json.dumps(batch_results, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
