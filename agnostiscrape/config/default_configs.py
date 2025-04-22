"""Default configuration dataclasses for AgnostiScrape.ai"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Tuple, Set, Callable, TypeVar, Generic, Literal

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