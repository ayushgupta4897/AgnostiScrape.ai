"""Gemini VLM client for AgnostiScrape.ai"""

from PIL import Image
from google import genai
from google.genai import types
import os
import logging

logger = logging.getLogger("agnostiscrape")

# Initialize the client with the API key
def initialize_client():
    """Initialize the Gemini client with API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY environment variable not set. VLM functionality will not work.")
        return None
    return genai.Client(api_key=api_key)

# Global client instance
client = initialize_client()

async def query_image_path(image_path: str, query: str, model: str = "gemini-2.0-flash"):
    """
    Process an image with Gemini VLM using the provided prompt.
    
    Args:
        image_path: Path to the image file
        query: Prompt to send to the model
        model: Gemini model to use
        
    Returns:
        Text response from the model
    """
    try:
        # Check if API key is set
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("Cannot query VLM: GEMINI_API_KEY environment variable not set")
            return "ERROR: API key not configured. Please set GEMINI_API_KEY environment variable."
        
        # Initialize client if not already initialized
        global client
        if client is None:
            client = genai.Client(api_key=api_key)
        
        # Open and read the image file
        image = Image.open(image_path)
        
        # Call the Gemini API with the image
        response = client.models.generate_content(
            model=model,
            contents=types.Content(
                parts=[
                    types.Part(
                        inline_data=types.Blob(
                            data=open(image_path, "rb").read(),
                            mime_type="image/jpeg"
                        )
                    ),
                    types.Part(text=query)
                ]
            )
        )
        
        return response.text
    except Exception as e:
        logger.error(f"Error querying VLM: {e}")
        return f"ERROR: {str(e)}"

def available_models():
    """
    List available Gemini models.
    
    Returns:
        List of available model names
    """
    try:
        # Check if API key is set
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("Cannot list models: GEMINI_API_KEY environment variable not set")
            return []
        
        # Initialize client if not already initialized
        global client
        if client is None:
            client = genai.Client(api_key=api_key)
            
        return [model.name for model in client.list_models() if "gemini" in model.name.lower()]
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return [] 