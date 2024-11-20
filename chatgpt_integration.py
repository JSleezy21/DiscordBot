import openai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_chatgpt_response(prompt):
    """
    Get a response from ChatGPT for a given prompt.
    :param prompt: User input string.
    :return: ChatGPT's response string.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Donald Trump and very full of yourself."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.7
        )
        logger.info("Successfully fetched response from ChatGPT.")
        return response.choices[0].message['content']
    except Exception as e:
        logger.error(f"Error communicating with ChatGPT: {e}")
        return "Sorry, I couldn't process your request."
