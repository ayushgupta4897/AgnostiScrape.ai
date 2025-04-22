from PIL import Image
from google import genai
from google.genai import types
import os

# Initialize the client with the API key
# For production, consider using environment variables for the API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def query_image_path(image_path : str, query: str, model="gemini-2.0-flash"):
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

def available_models():
    return [model.name for model in client.list_models() if "gemini" in model.name.lower()]