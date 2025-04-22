"""
Streamlit web UI for AgnostiScrape.ai

This provides a user-friendly interface for extracting structured data from websites
using AgnostiScrape.ai and displays the results.
"""

import streamlit as st
import asyncio
import json
import os
import logging
import time
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agnostiscrape-ui")

# Load environment variables from .env file (for GEMINI_API_KEY)
load_dotenv()

# Check API key in session state first (in case user entered it in the UI)
if "GEMINI_API_KEY" in st.session_state:
    os.environ["GEMINI_API_KEY"] = st.session_state["GEMINI_API_KEY"]

# Import AgnostiScrape components
from agnostiscrape import WebsiteScreenshotVLM, ScreenshotConfig, VLMConfig, StorageConfig

# Enable asyncio for Streamlit
async def run_scraper(urls, data_type, config_options):
    """Run the scraper with the given URLs and configuration"""
    # Configure the scraper based on user inputs
    scraper = WebsiteScreenshotVLM(
        screenshot_config=ScreenshotConfig(
            headless=True,
            browser_types=config_options["browser_types"],
            viewport_width=config_options["viewport_width"],
            viewport_height=config_options["viewport_height"],
            timeout_seconds=config_options["timeout_seconds"],
            post_load_delay_ms=config_options["post_load_delay_ms"],
            max_retries=config_options["max_retries"]
        ),
        storage_config=StorageConfig(
            output_dir=config_options["output_dir"],
            cleanup_screenshots=config_options["cleanup_screenshots"]
        ),
        max_concurrent=config_options["max_concurrent"]
    )
    
    if len(urls) == 1:
        # Single URL processing
        result = await scraper.process_url(urls[0], data_type)
        return {urls[0]: result}
    else:
        # Batch processing
        results = await scraper.process_batch(urls, data_type)
        return results

def format_results_as_dataframe(results: Dict[str, Dict[str, Any]], data_type: str) -> pd.DataFrame:
    """Format the results as a DataFrame for display"""
    formatted_data = []
    
    for url, data in results.items():
        row = {"URL": url}
        
        # Add error if present
        if "error" in data:
            row["Status"] = "Error"
            row["Error"] = data["error"]
            formatted_data.append(row)
            continue
        
        # Add status
        row["Status"] = "Success"
        
        # Add data based on data type
        if data_type == "product":
            row["Product Name"] = data.get("product_name", "N/A")
            row["Price"] = data.get("price", "N/A")
            row["Rating"] = data.get("rating", "N/A")
            row["Reviews"] = data.get("num_reviews", "N/A")
            row["Availability"] = data.get("availability", "N/A")
        elif data_type == "article":
            row["Title"] = data.get("title", "N/A")
            row["Author"] = data.get("author", "N/A")
            row["Date"] = data.get("date_published", "N/A")
            row["Source"] = data.get("source", "N/A")
        elif data_type == "real_estate":
            row["Property Type"] = data.get("property_type", "N/A")
            row["Address"] = data.get("address", "N/A")
            row["Price"] = data.get("price", "N/A")
            row["Bedrooms"] = data.get("bedrooms", "N/A")
            row["Bathrooms"] = data.get("bathrooms", "N/A")
            row["Square Footage"] = data.get("square_footage", "N/A")
        
        formatted_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(formatted_data)
    return df

def load_prompt_templates():
    """Load available prompt templates from the prompts directory"""
    # Find the prompts directory
    prompts_dir = Path(__file__).parent / "prompts"
    if not prompts_dir.exists():
        return ["product", "article"]  # Fallback to defaults
    
    # Get available prompt types from file names
    prompt_types = [f.stem for f in prompts_dir.glob("*.prompt")]
    if not prompt_types:
        return ["product", "article"]  # Fallback to defaults
    
    return prompt_types

def save_api_key_to_env(api_key):
    """Save API key to .env file"""
    try:
        env_path = Path(".env")
        
        # Check if .env exists
        if env_path.exists():
            # Read existing content
            with open(env_path, "r") as f:
                lines = f.readlines()
            
            # Check if GEMINI_API_KEY already exists
            key_exists = False
            for i, line in enumerate(lines):
                if line.startswith("GEMINI_API_KEY="):
                    lines[i] = f"GEMINI_API_KEY={api_key}\n"
                    key_exists = True
                    break
            
            # Add key if it doesn't exist
            if not key_exists:
                lines.append(f"GEMINI_API_KEY={api_key}\n")
            
            # Write back to file
            with open(env_path, "w") as f:
                f.writelines(lines)
        else:
            # Create new .env file
            with open(env_path, "w") as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
        
        return True
    except Exception as e:
        logger.error(f"Error saving API key to .env: {e}")
        return False

def main():
    st.set_page_config(
        page_title="AgnostiScrape.ai - Visual Web Scraping",
        page_icon="🔍",
        layout="wide",
    )
    
    # Header
    st.title("🔍 AgnostiScrape.ai")
    st.subheader("URL in, structured data out — no selectors to maintain, no DOM dependencies")
    
    # Check if API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        # Create a container for the API key input
        api_key_container = st.container(border=True)
        with api_key_container:
            st.error("⚠️ Gemini API Key is not set. You need to set up your API key to use this application.")
            st.markdown("""
            ### Set up your Gemini API Key
            
            1. **Get an API key**: Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a new API key
            2. **Enter your API key below** or add it to a `.env` file in the project root
            """)
            
            # Add API key input
            api_key_input = st.text_input(
                "Enter your Gemini API Key",
                type="password",
                placeholder="XXXX...XXXX",
                help="Your API key will be saved temporarily in this session"
            )
            
            # Option to save to .env file (more persistent)
            save_to_env = st.checkbox("Save API key to .env file", value=True, 
                                     help="This will save your API key to a .env file for future use")
            
            # Button to set API key
            if st.button("Set API Key", use_container_width=True, type="primary"):
                if api_key_input:
                    # Save to session state
                    st.session_state["GEMINI_API_KEY"] = api_key_input
                    
                    # Set environment variable
                    os.environ["GEMINI_API_KEY"] = api_key_input
                    
                    # Save to .env file if selected
                    if save_to_env:
                        if save_api_key_to_env(api_key_input):
                            st.success("API key saved to .env file!")
                        else:
                            st.warning("Failed to save API key to .env file. It will be available for this session only.")
                    
                    st.success("API key set successfully! Reload the page to continue.")
                    st.rerun()
                else:
                    st.error("Please enter your API key")
            
            # Show test script option
            st.info("If you've already set up your API key in a .env file, you can test it by running: `python test_gemini_api.py`")
        
        # Don't show the main app UI if API key is not set
        st.stop()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Data type selection
        available_data_types = load_prompt_templates()
        data_type = st.selectbox(
            "Data Type to Extract",
            options=available_data_types,
            index=available_data_types.index("product") if "product" in available_data_types else 0,
            help="Select the type of data to extract from the websites"
        )
        
        st.subheader("Advanced Options")
        
        # Browser options
        browser_col1, browser_col2 = st.columns(2)
        with browser_col1:
            browsers = st.multiselect(
                "Browsers",
                options=["chromium", "firefox", "webkit"],
                default=["chromium", "firefox"],
                help="Browsers to use for capturing screenshots"
            )
        with browser_col2:
            max_concurrent = st.number_input(
                "Concurrent URLs",
                min_value=1,
                max_value=10,
                value=2,
                help="Number of URLs to process concurrently"
            )
        
        # Viewport options
        viewport_col1, viewport_col2 = st.columns(2)
        with viewport_col1:
            viewport_width = st.number_input(
                "Viewport Width",
                min_value=800,
                max_value=3840,
                value=1920,
                step=100,
                help="Width of the browser viewport"
            )
        with viewport_col2:
            viewport_height = st.number_input(
                "Viewport Height",
                min_value=600,
                max_value=2160,
                value=1080,
                step=100,
                help="Height of the browser viewport"
            )
        
        # Timing options
        timing_col1, timing_col2 = st.columns(2)
        with timing_col1:
            timeout_seconds = st.number_input(
                "Timeout (seconds)",
                min_value=10,
                max_value=120,
                value=45,
                help="Maximum time to wait for page load"
            )
        with timing_col2:
            post_load_delay_ms = st.number_input(
                "Post-load Delay (ms)",
                min_value=500,
                max_value=10000,
                value=3000,
                step=500,
                help="Time to wait after page load"
            )
        
        # Other options
        max_retries = st.number_input(
            "Max Retries",
            min_value=0,
            max_value=5,
            value=2,
            help="Maximum number of retry attempts"
        )
        
        output_dir = st.text_input(
            "Output Directory",
            value="./screenshots",
            help="Directory to save screenshots and data"
        )
        
        cleanup_screenshots = st.checkbox(
            "Clean up Screenshots",
            value=False,
            help="Delete screenshots after processing"
        )
    
    # Main content area
    tab1, tab2 = st.tabs(["URL Input", "Results"])
    
    with tab1:
        st.subheader("Enter URLs to Scrape")
        
        input_method = st.radio(
            "Input Method",
            options=["Single URL", "Multiple URLs", "Upload File"],
            horizontal=True
        )
        
        urls = []
        
        if input_method == "Single URL":
            url = st.text_input("Enter URL", placeholder="https://www.example.com/product")
            if url:
                urls = [url]
                
        elif input_method == "Multiple URLs":
            url_text = st.text_area(
                "Enter URLs (one per line)",
                placeholder="https://www.example.com/product1\nhttps://www.example.com/product2"
            )
            if url_text:
                urls = [line.strip() for line in url_text.split("\n") if line.strip()]
                
        elif input_method == "Upload File":
            uploaded_file = st.file_uploader("Upload a file with URLs (one per line)", type=["txt", "csv"])
            if uploaded_file:
                content = uploaded_file.getvalue().decode("utf-8")
                urls = [line.strip() for line in content.split("\n") if line.strip()]
                st.info(f"Loaded {len(urls)} URLs from file")
        
        # Validation and submit button
        if len(urls) > 0:
            # Validate URLs
            valid_urls = []
            invalid_urls = []
            
            for url in urls:
                if url.startswith(("http://", "https://")):
                    valid_urls.append(url)
                else:
                    invalid_urls.append(url)
            
            if invalid_urls:
                st.warning(f"Found {len(invalid_urls)} invalid URLs (must start with http:// or https://)")
                with st.expander("Show invalid URLs"):
                    for url in invalid_urls:
                        st.text(url)
            
            if valid_urls:
                st.success(f"Ready to process {len(valid_urls)} URLs")
                
                # Configuration summary
                with st.expander("Configuration Summary"):
                    st.json({
                        "urls_count": len(valid_urls),
                        "data_type": data_type,
                        "browser_types": browsers,
                        "max_concurrent": max_concurrent,
                        "viewport": f"{viewport_width}x{viewport_height}",
                        "timeout": f"{timeout_seconds}s",
                        "post_load_delay": f"{post_load_delay_ms}ms",
                        "max_retries": max_retries,
                        "output_dir": output_dir,
                        "cleanup_screenshots": cleanup_screenshots
                    })
                
                # Start scraping button
                if st.button("Start Scraping", type="primary", use_container_width=True):
                    # Store configuration
                    config_options = {
                        "browser_types": browsers,
                        "viewport_width": viewport_width,
                        "viewport_height": viewport_height,
                        "timeout_seconds": timeout_seconds,
                        "post_load_delay_ms": post_load_delay_ms,
                        "max_retries": max_retries,
                        "output_dir": output_dir,
                        "cleanup_screenshots": cleanup_screenshots,
                        "max_concurrent": max_concurrent
                    }
                    
                    # Store the URLs and config in session state
                    st.session_state["urls"] = valid_urls
                    st.session_state["data_type"] = data_type
                    st.session_state["config"] = config_options
                    st.session_state["processing"] = True
                    st.session_state["start_time"] = time.time()
                    
                    # Switch to results tab
                    st.rerun()
    
    with tab2:
        if st.session_state.get("processing", False):
            st.subheader("Processing URLs...")
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            # Create placeholder for results
            results_container = st.container()
            
            with results_container:
                # Run the scraper
                with st.spinner("Scraping in progress..."):
                    urls = st.session_state["urls"]
                    data_type = st.session_state["data_type"]
                    config = st.session_state["config"]
                    
                    # Show URLs being processed
                    status_container.info(f"Processing {len(urls)} URLs...")
                    
                    # Run the scraper
                    try:
                        # Run the scraper and display progress
                        results = asyncio.run(run_scraper(urls, data_type, config))
                        
                        # Mark processing as complete
                        st.session_state["processing"] = False
                        st.session_state["results"] = results
                        
                        # Calculate elapsed time
                        elapsed_time = time.time() - st.session_state.get("start_time", time.time())
                        
                        # Show success message
                        status_container.success(f"Completed scraping {len(urls)} URLs in {elapsed_time:.2f} seconds")
                        progress_bar.progress(100)
                        
                        # Format and display results
                        st.subheader("Results")
                        df = format_results_as_dataframe(results, data_type)
                        st.dataframe(df, use_container_width=True)
                        
                        # Add download button for results
                        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                        st.download_button(
                            label="Download Results as CSV",
                            data=df.to_csv(index=False),
                            file_name=f"agnostiscrape_results_{timestamp}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                        # Add download button for raw JSON
                        st.download_button(
                            label="Download Raw JSON",
                            data=json.dumps(results, indent=2),
                            file_name=f"agnostiscrape_raw_{timestamp}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.session_state["processing"] = False
                        st.error(f"Error during scraping: {str(e)}")
                        logger.exception("Error during scraping")
        
        elif "results" in st.session_state:
            # Display previous results
            st.subheader("Previous Results")
            results = st.session_state["results"]
            data_type = st.session_state["data_type"]
            
            # Format and display results
            df = format_results_as_dataframe(results, data_type)
            st.dataframe(df, use_container_width=True)
            
            # Add download buttons
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="Download Results as CSV",
                    data=df.to_csv(index=False),
                    file_name=f"agnostiscrape_results_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="Download Raw JSON",
                    data=json.dumps(results, indent=2),
                    file_name=f"agnostiscrape_raw_{timestamp}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Add button to clear results
            if st.button("Clear Results", use_container_width=True):
                del st.session_state["results"]
                del st.session_state["data_type"]
                st.rerun()
        
        else:
            # No results yet
            st.info("Enter URLs in the 'URL Input' tab and click 'Start Scraping' to see results here.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center">
            <p>
                <small>
                    Powered by <b>AgnostiScrape.ai</b> - 
                    <a href="https://github.com/yourusername/AgnostiScrape.ai" target="_blank">GitHub</a>
                </small>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # Initialize session state
    if "processing" not in st.session_state:
        st.session_state["processing"] = False
    
    main() 