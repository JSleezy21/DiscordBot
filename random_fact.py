import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_random_fact():
    """Fetches a random fact from the API."""
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    try:
        logger.info("Fetching a random fact from the API.")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP status
        fact = response.json().get("text", "No fact found.")
        logger.info("Successfully fetched a random fact.")
        return fact
    except requests.RequestException as e:
        logger.error(f"Error fetching the random fact: {e}")
        return "Could not fetch a random fact at this time."
