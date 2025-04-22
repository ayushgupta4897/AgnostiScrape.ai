# AgnostiScrape.ai Streamlit UI

A web-based interface for using AgnostiScrape.ai - the zero-maintenance web data extraction tool.

## Overview

This Streamlit application provides a user-friendly interface for AgnostiScrape.ai, allowing you to:

- Extract structured data from any website without selectors or DOM dependencies
- Process single URLs or batches of URLs concurrently
- Configure all aspects of the scraping process
- Download results in CSV or JSON formats
- Visualize extracted data

## Installation

### From GitHub Repository

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AgnostiScrape.ai.git
cd AgnostiScrape.ai
```

2. Install the dependencies:
```bash
pip install -r streamlit_requirements.txt
```

3. Set up your Gemini API key:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Running the App

Start the Streamlit app with:

```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser.

## Usage Guide

### 1. Configuration

In the sidebar, you can configure:

- **Data Type**: Choose the type of data to extract (product, article, real estate, etc.)
- **Browser Options**: Select which browsers to use and concurrency level
- **Viewport Settings**: Configure the screenshot dimensions
- **Timing Settings**: Adjust timeouts and delays
- **Output Settings**: Choose where to save files and cleanup options

### 2. URL Input

There are three ways to input URLs:

- **Single URL**: Enter a single URL to process
- **Multiple URLs**: Enter multiple URLs in a text area (one per line)
- **Upload File**: Upload a text file with URLs (one per line)

### 3. Results

After processing, you'll see:

- A summary table of all extracted data
- Download options for CSV and JSON formats
- Links to any saved screenshots

## Example Use Cases

- **E-commerce Price Monitoring**: Track prices across multiple retailers
- **Real Estate Listing Data**: Extract property details from listing sites
- **Article Summarization**: Extract titles, authors, and summaries from news sites
- **Product Comparison**: Gather specifications from multiple product pages

## Troubleshooting

- **API Key Issues**: Ensure your Gemini API key is set correctly in the .env file
- **Browser Issues**: Make sure Playwright browsers are installed (`playwright install chromium firefox`)
- **URL Format**: All URLs must start with http:// or https://
- **Memory Issues**: For large batches, reduce the concurrency level

## Contributing

Contributions to improve the UI are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 