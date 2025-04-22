# AgnostiScrape.ai

URL in, structured data out in one step—**no selectors to maintain**, **no DOM dependencies**, **immune to site changes and obfuscation**.

## Overview

AgnostiScrape.ai transforms web scraping by leveraging pure visual intelligence, eliminating traditional dependencies and maintenance headaches.

### Vision-First Approach: Beyond DOM Limitations

Unlike traditional scrapers that break when websites change their HTML structure, class names, or IDs, AgnostiScrape.ai operates entirely on the visual layer:

- **Ignores DOM Completely**: No XPaths, CSS selectors, or element IDs to maintain
- **Processes What Humans See**: Uses the final rendered page, not the underlying code
- **Adapts to Redesigns**: Website layout changes don't require code updates since it understands content semantically

### Immune to Anti-Scraping Techniques

Modern websites employ sophisticated anti-bot measures that AgnostiScrape.ai bypasses:

- **Bypasses JavaScript Obfuscation**: Doesn't care if element IDs are randomized or dynamically generated
- **Handles CSS Tricks**: Immune to visibility tricks or honeypot elements
- **Ignores Code Structure**: No impact from minification, bundling, or framework changes

## Installation

```bash
pip install agnostiscrape
```

Or install from source:

```bash
git clone https://github.com/yourusername/AgnostiScrape.ai.git
cd AgnostiScrape.ai
pip install -e .
```

### Prerequisites

- Python 3.8+
- Playwright browsers (installed automatically)
- Gemini API key (for the VLM processing)

## Quick Start

First, set up your Gemini API key:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or you can use a `.env` file:

```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

### Extracting Data from a Product Page

```python
import asyncio
from agnostiscrape import WebsiteScreenshotVLM

async def main():
    # Create scraper with default configuration
    scraper = WebsiteScreenshotVLM()
    
    # Process a URL and get structured data
    result = await scraper.process_url(
        "https://www.amazon.com/Apple-MacBook-16-inch-10%E2%80%91core-16%E2%80%91core/dp/B0CM5JS1GQ/", 
        "product"
    )
    
    # Display the product data
    print(f"Product: {result.get('product_name')}")
    print(f"Price: {result.get('price')}")
    print(f"Rating: {result.get('rating')}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Batch Processing Multiple URLs

```python
import asyncio
from agnostiscrape import WebsiteScreenshotVLM

async def main():
    # Create scraper with increased concurrency
    scraper = WebsiteScreenshotVLM(max_concurrent=3)
    
    # List of URLs to process
    urls = [
        "https://www.amazon.com/product1",
        "https://www.bestbuy.com/product2",
        "https://www.walmart.com/product3"
    ]
    
    # Process all URLs concurrently
    results = await scraper.process_batch(urls, "product")
    
    # Display results
    for url, data in results.items():
        print(f"URL: {url}")
        print(f"Product: {data.get('product_name')}")
        print(f"Price: {data.get('price')}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

## Streamlit UI

AgnostiScrape.ai comes with a user-friendly Streamlit web interface for easy usage without writing code.

### Running the Streamlit UI

```bash
# Install Streamlit requirements
pip install -r streamlit_requirements.txt

# Run the app
streamlit run streamlit_app.py
```

### Features of the UI

- **User-friendly interface**: No coding required
- **Batch processing**: Process multiple URLs at once
- **Configuration options**: Easily adjust all scraper settings
- **Results visualization**: Display extracted data in tables
- **Export options**: Download results as CSV or JSON

![Streamlit UI Screenshot](https://your-image-url-here.png)

For more information about the UI, see [streamlit_app_README.md](streamlit_app_README.md).

## Configuration

AgnostiScrape.ai supports extensive configuration options:

### Screenshot Configuration

```python
from agnostiscrape import WebsiteScreenshotVLM
from agnostiscrape.config import ScreenshotConfig

scraper = WebsiteScreenshotVLM(
    screenshot_config=ScreenshotConfig(
        headless=True,                              # Run browsers in headless mode
        browser_types=["chromium", "firefox"],      # Browsers to try in order
        viewport_width=1920,                        # Screenshot width
        viewport_height=1080,                       # Screenshot height
        device_scale_factor=2.0,                    # For high DPI screenshots
        timeout_seconds=45,                         # Navigation timeout
        wait_until="domcontentloaded",              # When to consider navigation complete
        full_page=True,                             # Capture full page (not just viewport)
        post_load_delay_ms=3000,                    # Wait after page load
        max_retries=2                               # Retry attempts
    )
)
```

### VLM Configuration

```python
from agnostiscrape.config import VLMConfig

vlm_config = VLMConfig(
    # Custom prompt templates for different page types
    prompt_templates={
        "product": """Your custom product page prompt...""",
        "article": """Your custom article page prompt..."""
    },
    default_data_type="product"
)
```

### Storage Configuration

```python
from agnostiscrape.config import StorageConfig

storage_config = StorageConfig(
    output_dir="./screenshots",           # Directory to store screenshots
    cleanup_screenshots=False,            # Whether to delete screenshots after processing
    keep_days=7,                          # How long to keep files
    file_prefix="screenshot_",            # Prefix for screenshot filenames
    data_file_prefix="data_"              # Prefix for data filenames
)
```

## Supported Content Types

AgnostiScrape.ai comes with built-in support for:

- **Product Pages**: Extract product name, price, ratings, descriptions, etc.
- **Article Pages**: Extract titles, authors, publication dates, and summaries

You can easily add custom content types by adding a prompt file to the `prompts` directory or by configuring a custom `VLMConfig`.

## How It Works

1. **Screenshot Capture**: Uses Playwright to render and capture a screenshot of the target page
2. **Visual Processing**: Sends the screenshot to Gemini VLM with a specialized prompt
3. **Data Extraction**: VLM analyzes the visual content and extracts structured data in JSON format
4. **Result Processing**: Returns clean structured data ready for your application

## Advantages Over Traditional Scrapers

- **Zero Maintenance**: No need to update selectors when websites change
- **Works on Any Site**: From React SPAs to complex JavaScript applications
- **Robust Against Changes**: Continues working through site redesigns and updates
- **Bypasses Anti-Scraping**: Not affected by most anti-bot techniques
- **Framework Agnostic**: Works with any frontend technology

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
