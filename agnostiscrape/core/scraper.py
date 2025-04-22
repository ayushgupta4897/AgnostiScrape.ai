"""Main scraper functionality for AgnostiScrape.ai"""

import os
import json
import asyncio
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set

from ..config import ScreenshotConfig, VLMConfig, StorageConfig
from ..utils import generate_file_paths, cleanup_old_files, load_prompt_template
from .browser import BrowserManager

logger = logging.getLogger("agnostiscrape")

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
        
        # Initialize browser manager
        self.browser_manager = BrowserManager(
            headless=self.screenshot_config.headless,
            browser_args=self.screenshot_config.browser_args
        )
        
        # Create output directory
        os.makedirs(self.storage_config.output_dir, exist_ok=True)
        
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
                    screenshot = await self.browser_manager.capture_screenshot(
                        url=url,
                        browser_type=browser_type,
                        viewport_width=self.screenshot_config.viewport_width,
                        viewport_height=self.screenshot_config.viewport_height,
                        user_agent=self.screenshot_config.user_agent,
                        locale=self.screenshot_config.locale,
                        timezone_id=self.screenshot_config.timezone_id,
                        device_scale_factor=self.screenshot_config.device_scale_factor,
                        extra_headers=self.screenshot_config.extra_headers,
                        wait_until=self.screenshot_config.wait_until,
                        timeout_ms=self.screenshot_config.timeout_seconds * 1000,
                        post_load_delay_ms=self.screenshot_config.post_load_delay_ms,
                        scroll_percent=self.screenshot_config.scroll_percent,
                        full_page=self.screenshot_config.full_page
                    )
                    
                    if screenshot:
                        return screenshot
            
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
                from ..clients import query_image_path
                
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
        # First try to load from file
        prompt = load_prompt_template(data_type)
        
        # If not found in file, try from config
        if not prompt:
            prompt = self.vlm_config.prompt_templates.get(
                data_type, 
                self.vlm_config.prompt_templates[self.vlm_config.default_data_type]
            )
            
        return prompt
    
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
        screenshot_path, data_path = generate_file_paths(
            url, 
            self.storage_config.output_dir,
            self.storage_config.file_prefix,
            self.storage_config.data_file_prefix
        )
        
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
        await cleanup_old_files(
            self.storage_config.output_dir,
            self.storage_config.file_prefix,
            self.storage_config.data_file_prefix,
            self.storage_config.keep_days,
            self.storage_config.cleanup_screenshots
        )
        
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