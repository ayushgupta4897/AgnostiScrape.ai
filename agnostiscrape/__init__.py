"""
AgnostiScrape.ai - URL in, structured data out in one step

A vision-first approach to web scraping, eliminating traditional DOM dependencies
and maintenance headaches by leveraging visual intelligence (VLM).
"""

from .core.scraper import WebsiteScreenshotVLM
from .config import ScreenshotConfig, VLMConfig, StorageConfig

__version__ = "0.1.0"
__all__ = ["WebsiteScreenshotVLM", "ScreenshotConfig", "VLMConfig", "StorageConfig"] 