import openai
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_image(prompt):
    """
    Generate an AI image based on the prompt using OpenAI's API.
    :param prompt: The textual description for the image.
    :return: URL of the generated image or an error message.
    """
    try:
        logger.info(f"Generating image for prompt: {prompt}")
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        logger.info("Image generated successfully")
        return image_url
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return "An error occurred while generating the image. Please try again later."
