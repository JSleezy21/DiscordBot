import os
import random
import string
import sqlite3
from cryptography.fernet import Fernet
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate or load encryption key
def load_key():
    key_file = "secret.key"
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, "wb") as keyfile:
            keyfile.write(key)
    else:
        with open(key_file, "rb") as keyfile:
            key = keyfile.read()
    return key

fernet = Fernet(load_key())

# Database setup
DB_NAME = "passwords.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            user_id TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

setup_database()

def generate_password(length=None):
    """
    Generate a secure random password.
    :param length: The desired length of the password (default between 12 and 30).
    :return: A random password.
    """
    if not length:
        length = random.randint(12, 30)  # Random length between 12 and 30
    elif length < 12:
        length = 12
    elif length > 30:
        length = 30

    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    logger.info(f"Password of length {length} generated successfully")
    return password

def store_password(user_id, password):
    """Encrypt and store the password."""
    encrypted_password = fernet.encrypt(password.encode())
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO passwords (user_id, password) VALUES (?, ?)", (user_id, encrypted_password))
    conn.commit()
    conn.close()
    logger.info(f"Password for user {user_id} stored successfully")

def retrieve_password(user_id):
    """Retrieve and decrypt the password for a user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM passwords WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        decrypted_password = fernet.decrypt(result[0]).decode()
        logger.info(f"Password for user {user_id} retrieved successfully")
        return decrypted_password
    else:
        logger.warning(f"No password found for user {user_id}")
        return None
