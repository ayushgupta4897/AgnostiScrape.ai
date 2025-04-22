"""Storage and file management utilities for AgnostiScrape.ai"""

import os
import time
import hashlib
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger("agnostiscrape")

def generate_file_paths(url: str, output_dir: str, file_prefix: str, data_prefix: str) -> Tuple[str, str]:
    """
    Generate file paths for screenshot and data files.
    
    Args:
        url: URL to generate paths for
        output_dir: Directory to store files
        file_prefix: Prefix for screenshot files
        data_prefix: Prefix for data files
        
    Returns:
        Tuple of (screenshot_path, data_path)
    """
    # Create hash of URL for filename
    url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
    
    # Generate paths
    screenshot_path = os.path.join(
        output_dir, 
        f"{file_prefix}{url_hash}.png"
    )
    data_path = os.path.join(
        output_dir, 
        f"{data_prefix}{url_hash}.json"
    )
    
    return screenshot_path, data_path

async def cleanup_old_files(output_dir: str, file_prefix: str, data_prefix: str, keep_days: int, should_cleanup: bool) -> None:
    """
    Clean up old screenshot and data files.
    
    Args:
        output_dir: Directory containing files
        file_prefix: Prefix for screenshot files
        data_prefix: Prefix for data files
        keep_days: Number of days to keep files
        should_cleanup: Whether to clean up files
    """
    if not should_cleanup:
        return
    
    try:
        now = time.time()
        max_age = keep_days * 24 * 60 * 60
        
        for filename in os.listdir(output_dir):
            if filename.startswith(file_prefix) or \
               filename.startswith(data_prefix):
                file_path = os.path.join(output_dir, filename)
                
                # Get file age
                file_age = now - os.path.getmtime(file_path)
                
                # Remove if too old
                if file_age > max_age:
                    logger.info(f"Removing old file: {file_path}")
                    os.remove(file_path)
    
    except Exception as e:
        logger.error(f"Error cleaning up old files: {e}")

def load_prompt_template(data_type: str) -> str:
    """
    Load a prompt template from the prompts directory.
    
    Args:
        data_type: Type of data/prompt to load
        
    Returns:
        Prompt template string
    """
    # Determine prompts directory based on package location
    package_dir = Path(__file__).resolve().parent.parent.parent
    prompt_file = package_dir / "prompts" / f"{data_type}.prompt"
    
    # Load prompt from file if it exists
    if prompt_file.exists():
        with open(prompt_file, "r") as f:
            return f.read()
    else:
        logger.warning(f"Prompt file not found: {prompt_file}")
        # Return empty string if file not found
        return "" 