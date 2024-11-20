import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Headers to mimic a legitimate browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json",
}

def lookup_ip(ip_address):
    """
    Perform an IP lookup using ipapi.co.
    :param ip_address: The IP address to look up.
    :return: A formatted string with IP details or an error message.
    """
    try:
        url = f"https://ipapi.co/{ip_address}/json/"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            logger.error(f"Failed to fetch IP info: {response.status_code} - {response.text}")
            return "Error fetching IP details. Please try again later."

        data = response.json()
        ip = data.get("ip", "N/A")
        city = data.get("city", "N/A")
        region = data.get("region", "N/A")
        country = data.get("country_name", "N/A")
        org = data.get("org", "N/A")
        latitude = data.get("latitude", "N/A")
        longitude = data.get("longitude", "N/A")

        logger.info(f"IP lookup successful for {ip_address}")
        return (
            f"**IP Address:** {ip}\n"
            f"**City:** {city}\n"
            f"**Region:** {region}\n"
            f"**Country:** {country}\n"
            f"**Organization:** {org}\n"
            f"**Latitude/Longitude:** {latitude}, {longitude}"
        )
    except Exception as e:
        logger.error(f"Error during IP lookup: {e}")
        return "An error occurred during the IP lookup. Please try again later."
