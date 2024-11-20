import discord
import random
from discord.ext import commands, tasks
from random_fact import get_random_fact
import logging
from dotenv import load_dotenv
import os
from calculator import calculate
from twitch_notifier import check_stream_status, update_live_status
from chatgpt_integration import get_chatgpt_response
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from datetime import datetime
from ip_lookup import lookup_ip
from password_manager import generate_password, store_password, retrieve_password
from ai_image_generator import generate_image
from weather_module import get_weather
from vulnerability_scan import scan_ip


# Load environment variables
load_dotenv()

# Get the Discord token from the .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NOTIFY_CHANNEL_ID = int(os.getenv("NOTIFY_CHANNEL_ID"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Initialize the bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
intents.message_content = True  # Enable message content access
client = discord.Client(intents=intents)
geolocator = Nominatim(user_agent="timezone_bot")
tf = TimezoneFinder()

# Sync slash commands
@bot.event
async def on_ready():
    """Triggered when the bot is ready and slash commands are synced."""
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash commands.")
        logger.info(f"{bot.user.name} is now running!")
        monitor_streams.start()
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

# Monitor Twitch streams periodically
@tasks.loop(seconds=30)
async def monitor_streams():
    """Check Twitch streams and send notifications if live."""
    twitch_usernames = ["spiffypolecat", "kota9113","jsleezy_stream"]  # Replace with actual usernames
    channel = bot.get_channel(NOTIFY_CHANNEL_ID)
    if not channel:
        logger.error(f"Notification channel with ID {NOTIFY_CHANNEL_ID} not found.")
        return
    for username in twitch_usernames:
        is_live, stream_details = check_stream_status(username)
        if update_live_status(username, is_live):
            logger.info(f"{username} is live! Notifying channel.")
            await channel.send(
                f"{username} is live on Twitch! \n"
                f"Title: {stream_details['title']}\n"
                f"Watch here: https://www.twitch.tv/{username}"
            )
        elif not is_live:
            logger.info(f"{username} is not live or already notified.")

# Define a command to get a random fact
@bot.event
async def on_message(message):
    """Handle incoming messages."""
    if message.author == bot.user:
        return

    # Command to get a random fact
    if message.content.lower() == "!fact":
        logger.info(f"User {message.author} requested a random fact.")
        fact = get_random_fact()
        await message.channel.send(f"Here's a random fact: {fact}")

    if message.content.startswith("!lookup_ip"):
        ip_address = message.content[len("!lookup_ip "):].strip()
        if not ip_address:
            await message.channel.send("Please provide an IP address. Usage: `!lookup_ip <IP>`")
            return

        logger.info(f"User {message.author} requested IP lookup for: {ip_address}")
        result = lookup_ip(ip_address)
        await message.channel.send(result)

    # Check if the message starts with "!time"
    if message.content.startswith("!time"):
        # Extract location from the message, defaulting to "UTC" if none is provided
        location = message.content[len("!time"):].strip() or "UTC"

        try:
            # Attempt to locate the place with GeoPy
            place = geolocator.geocode(location)
            if place:
                # Get the timezone based on latitude and longitude
                timezone_str = tf.timezone_at(lng=place.longitude, lat=place.latitude)
                if timezone_str:
                    tz = pytz.timezone(timezone_str)
                    current_time = datetime.now(tz)
                    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
                    await message.channel.send(f"The current time in {location} is: {formatted_time}")
                else:
                    await message.channel.send("Sorry, I couldn't determine the timezone for that location.")
            else:
                await message.channel.send("Location not found. Please provide a valid city, state, or country.")
        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")

    if message.content.startswith("!chat"):
        user_query = message.content[len("!chat "):]  # Extract the query after !chat
        if not user_query.strip():
            await message.channel.send("Please provide a prompt for ChatGPT. Usage: `!chat <your question>`")
            return

        logger.info(f"User {message.author} requested ChatGPT response: {user_query}")
        response = get_chatgpt_response(user_query)
        await message.channel.send(response)

        # Check if the message starts with "!roll"

    if message.content.startswith("!password"):
        try:
            parts = message.content.split()
            length = int(parts[1]) if len(parts) > 1 else None
            password = generate_password(length)
            user_id = str(message.author.id)
            store_password(user_id, password)
            await message.author.send(f"Your generated password is: {password}")
            await message.channel.send("Password sent to your direct messages!")
        except ValueError:
            await message.channel.send("Invalid length. Usage: `!generate_password [length]`")

    elif message.content.startswith("!get_password"):
        user_id = str(message.author.id)
        password = retrieve_password(user_id)
        if password:
            await message.author.send(f"Your stored password is: {password}")
        else:
            await message.channel.send("No password found for your user ID.")

    elif message.content.startswith("!roll"):
        # Roll a d20
        roll_result = random.choice(range(1, 21))
        await message.channel.send(f"You rolled a d20 and got: {roll_result}")

    if message.content.startswith("!image"):
        prompt = message.content[len("!image "):].strip()
        if not prompt:
            await message.channel.send(
                "Please provide a description for the image. Usage: `!generate_image <description>`")
            return

        await message.channel.send("Generating your image, please wait...")
        image_url = generate_image(prompt)
        if "http" in image_url:
            await message.channel.send(f"Here is your image: {image_url}")
        else:
            await message.channel.send(image_url)

    if message.content.startswith("!weather"):
        city_name = message.content[len("!weather "):].strip()
        if not city_name:
            await message.channel.send("Please provide a city name. Usage: `!weather <city>`")
            return

        await message.channel.send("Fetching weather, please wait...")
        weather_info = get_weather(city_name)
        await message.channel.send(weather_info)

    if message.content.startswith("!scan"):
        ip_address = message.content[len("!scan "):].strip()
        if not ip_address:
            await message.channel.send("Please provide an IP address. Usage: `!scan <IP>`")
            return

        # Acknowledge the scan in the channel
        await message.channel.send(
            f"Scanning IP: {ip_address}, results will be sent to your DM. This may take a while...")

        try:
            # Perform the scan
            scan_results = scan_ip(ip_address)

            # Send results via DM
            await message.author.send(f"Results of the scan for IP {ip_address}:\n\n{scan_results}")
            logger.info(f"Scan results for {ip_address} sent to {message.author}.")
        except discord.Forbidden:
            # Handle case where DMs are disabled
            await message.channel.send("I couldn't send you a DM. Please enable direct messages and try again.")
            logger.warning(f"Failed to send DM to {message.author}. Direct messages may be disabled.")
        except Exception as e:
            # General error handling
            await message.channel.send("An unexpected error occurred while performing the scan.")
            logger.error(f"Error during scan or sending results: {e}")

    else:
        logger.info(f"Ignored message: {message.content}")

# Slash command: Calculate a mathematical expression
@bot.tree.command(name="calculate", description="Evaluate a mathematical expression.")
async def calculate_command(interaction: discord.Interaction, expression: str):
    """
    Slash command to calculate a mathematical expression.
    """
    logger.info(f"User {interaction.user} requested a calculation: {expression}")
    result = calculate(expression)
    await interaction.response.send_message(f"Result: {result}")



# Start the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
