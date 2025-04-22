"""Test the configuration classes"""

import unittest
from agnostiscrape.config import ScreenshotConfig, VLMConfig, StorageConfig

class TestConfigs(unittest.TestCase):
    """Test the configuration classes"""
    
    def test_screenshot_config_defaults(self):
        """Test ScreenshotConfig default values"""
        config = ScreenshotConfig()
        self.assertTrue(config.headless)
        self.assertEqual(config.browser_types, ["chromium", "firefox"])
        self.assertEqual(config.viewport_width, 1920)
        self.assertEqual(config.viewport_height, 1080)
        self.assertEqual(config.wait_until, "domcontentloaded")
        
    def test_vlm_config_defaults(self):
        """Test VLMConfig default values"""
        config = VLMConfig()
        self.assertEqual(config.default_data_type, "product")
        self.assertIn("product", config.prompt_templates)
        self.assertIn("article", config.prompt_templates)
        
    def test_storage_config_defaults(self):
        """Test StorageConfig default values"""
        config = StorageConfig()
        self.assertEqual(config.output_dir, "./screenshots")
        self.assertFalse(config.cleanup_screenshots)
        self.assertEqual(config.keep_days, 7)
        
    def test_custom_screenshot_config(self):
        """Test custom ScreenshotConfig values"""
        config = ScreenshotConfig(
            headless=False,
            browser_types=["webkit"],
            viewport_width=1280,
            viewport_height=720
        )
        self.assertFalse(config.headless)
        self.assertEqual(config.browser_types, ["webkit"])
        self.assertEqual(config.viewport_width, 1280)
        self.assertEqual(config.viewport_height, 720)
        
if __name__ == "__main__":
    unittest.main() 