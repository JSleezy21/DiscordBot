import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twitch API credentials
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
BASE_TWITCH_URL = "https://api.twitch.tv/helix"
access_token = None

# Dictionary to track streamers' live statuses
live_streams = {}

def get_twitch_access_token():
    """Get a Twitch API access token."""
    global access_token
    if not access_token:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logger.info("Successfully obtained Twitch access token.")
    return access_token

def check_stream_status(username):
    """
    Check if a Twitch streamer is live.
    :param username: Twitch username of the streamer.
    :return: Boolean indicating live status and stream details.
    """
    global access_token
    url = f"{BASE_TWITCH_URL}/streams"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_twitch_access_token()}",
    }
    params = {"user_login": username}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 401:  # Token expired, refresh it
        logger.warning("Twitch access token expired. Refreshing...")
        access_token = None
        return check_stream_status(username)
    response.raise_for_status()
    data = response.json().get("data", [])
    if data:
        return True, data[0]  # Stream is live, return stream details
    return False, None

def update_live_status(username, is_live):
    """
    Update the live status of a streamer and determine if a notification is needed.
    :param username: Twitch username of the streamer.
    :param is_live: Boolean indicating current live status.
    :return: Boolean indicating if a notification should be sent.
    """
    was_live = live_streams.get(username, False)
    live_streams[username] = is_live
    return is_live and not was_live