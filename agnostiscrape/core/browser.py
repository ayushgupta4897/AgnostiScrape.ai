"""Browser management functionality for AgnostiScrape.ai"""

import logging
import asyncio
from typing import Optional, Tuple, Literal
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response

logger = logging.getLogger("agnostiscrape")

BrowserType = Literal["chromium", "firefox", "webkit"]

class BrowserManager:
    """
    Manages browser instances for screenshot capture.
    Provides utilities for initializing browsers, handling contexts, and taking screenshots.
    """
    
    def __init__(self, headless: bool = True, browser_args: list = None):
        """
        Initialize the BrowserManager.
        
        Args:
            headless: Whether to run browsers in headless mode
            browser_args: Arguments to pass to the browser
        """
        self.headless = headless
        self.browser_args = browser_args or []
        
    async def initialize_browser(self, browser_type_name: BrowserType, 
                                 viewport_width: int, viewport_height: int,
                                 user_agent: str, locale: str, timezone_id: str, 
                                 device_scale_factor: float = 1.0) -> Tuple[Browser, BrowserContext]:
        """
        Initialize a browser and context with the given configuration.
        
        Args:
            browser_type_name: Type of browser to launch
            viewport_width: Width of the viewport
            viewport_height: Height of the viewport
            user_agent: User agent string
            locale: Locale to use
            timezone_id: Timezone ID
            device_scale_factor: Device scale factor
            
        Returns:
            Tuple of browser and browser context
        """
        async with async_playwright() as playwright:
            # Get browser type object
            browser_type = getattr(playwright, browser_type_name)
            
            # Launch browser with configuration
            browser = await browser_type.launch(
                headless=self.headless,
                args=self.browser_args
            )
            
            # Create context with configuration
            context = await browser.new_context(
                viewport={
                    "width": viewport_width, 
                    "height": viewport_height
                },
                user_agent=user_agent,
                locale=locale,
                timezone_id=timezone_id,
                device_scale_factor=device_scale_factor
            )
            
            # Add script to mask automation
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                window.chrome = { runtime: {} };
            """)
            
            return browser, context
            
    async def capture_screenshot(self, url: str, 
                                browser_type: BrowserType,
                                viewport_width: int, 
                                viewport_height: int,
                                user_agent: str, 
                                locale: str, 
                                timezone_id: str,
                                device_scale_factor: float,
                                extra_headers: dict,
                                wait_until: str,
                                timeout_ms: int,
                                post_load_delay_ms: int,
                                scroll_percent: float,
                                full_page: bool) -> Optional[bytes]:
        """
        Capture a screenshot of the given URL.
        
        Args:
            url: URL to capture
            browser_type: Type of browser to use
            viewport_width: Width of the viewport
            viewport_height: Height of the viewport
            user_agent: User agent string
            locale: Locale to use
            timezone_id: Timezone ID
            device_scale_factor: Device scale factor
            extra_headers: Extra headers to send with the request
            wait_until: When to consider navigation complete
            timeout_ms: Timeout for navigation in milliseconds
            post_load_delay_ms: Delay after page load in milliseconds
            scroll_percent: How far to scroll down the page (0.0-1.0)
            full_page: Whether to capture the full page or just the viewport
            
        Returns:
            Screenshot bytes if successful, None otherwise
        """
        browser = None
        
        try:
            async with async_playwright() as p:
                # Get browser type object
                browser_type_obj = getattr(p, browser_type)
                
                # Launch browser with configuration
                browser = await browser_type_obj.launch(
                    headless=self.headless,
                    args=self.browser_args
                )
                
                # Create context with configuration
                context = await browser.new_context(
                    viewport={
                        "width": viewport_width, 
                        "height": viewport_height
                    },
                    user_agent=user_agent,
                    locale=locale,
                    timezone_id=timezone_id,
                    device_scale_factor=device_scale_factor
                )
                
                # Add script to mask automation
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => false });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    window.chrome = { runtime: {} };
                """)
                
                # Create page with headers
                page = await context.new_page()
                await page.set_extra_http_headers(extra_headers)
                
                # Navigate to URL
                logger.info(f"Navigating to {url} with {browser_type}")
                response = await page.goto(
                    url, 
                    wait_until=wait_until, 
                    timeout=timeout_ms
                )
                
                # Check response status
                if not response or response.status >= 400:
                    logger.warning(f"Failed to load {url}: {response.status if response else 'No response'}")
                    await browser.close()
                    return None
                
                # Wait for additional content to load
                await page.wait_for_timeout(post_load_delay_ms)
                
                # Scroll to simulate user behavior
                await page.evaluate(f"""
                    window.scrollTo({{
                        top: document.body.scrollHeight * {scroll_percent},
                        behavior: 'smooth'
                    }});
                """)
                await page.wait_for_timeout(1000)
                
                # Scroll back to top
                await page.evaluate("window.scrollTo(0, 0);")
                await page.wait_for_timeout(500)
                
                # Take screenshot
                logger.info(f"Taking screenshot of {url}")
                screenshot = await page.screenshot(full_page=full_page)
                
                # Close browser
                await browser.close()
                
                return screenshot
        
        except Exception as e:
            logger.error(f"Error capturing {url} with {browser_type}: {e}")
            if browser:
                try:
                    await browser.close()
                except:
                    pass
            return None 