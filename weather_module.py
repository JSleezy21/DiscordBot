import requests
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenWeatherMap API key
API_KEY = os.getenv("WEATHER_API_KEY")
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_coordinates(city_name):
    """
    Fetches latitude and longitude for a city.
    :param city_name: Name of the city.
    :return: A tuple (latitude, longitude) or None if not found.
    """
    try:
        logger.info(f"Fetching coordinates for city: {city_name}")
        params = {"q": city_name, "appid": API_KEY}
        response = requests.get(GEO_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            logger.error(f"City '{city_name}' not found.")
            return None

        lat, lon = data[0]["lat"], data[0]["lon"]
        logger.info(f"Coordinates for {city_name}: ({lat}, {lon})")
        return lat, lon
    except Exception as e:
        logger.error(f"Error fetching coordinates: {e}")
        return None

def get_weather(city_name):
    """
    Fetches the current weather for a given city using its coordinates.
    :param city_name: Name of the city.
    :return: A string containing weather information or an error message.
    """
    try:
        # Get city coordinates
        coordinates = get_coordinates(city_name)
        if not coordinates:
            return "City not found. Please check the name and try again."

        lat, lon = coordinates
        logger.info(f"Fetching weather for coordinates: ({lat}, {lon})")
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "imperial"}
        response = requests.get(WEATHER_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract weather details
        city = data["name"]
        country = data["sys"]["country"]
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_info = (
            f"Weather in {city}, {country}:\n"
            f"- Temperature: {temperature}°F\n"
            f"- Condition: {weather_description.capitalize()}\n"
            f"- Humidity: {humidity}%\n"
            f"- Wind Speed: {wind_speed} m/s"
        )
        logger.info("Weather data fetched successfully")
        return weather_info

    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return "An unexpected error occurred while fetching weather data."
