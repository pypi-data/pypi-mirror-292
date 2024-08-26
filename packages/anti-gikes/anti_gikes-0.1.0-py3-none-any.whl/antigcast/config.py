import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(".env")

# Print environment variables for debugging
print(f"BOT_TOKEN: {os.environ.get('BOT_TOKEN')}")
print(f"BOT_WORKERS: {os.environ.get('BOT_WORKERS')}")
print(f"APP_ID: {os.environ.get('APP_ID')}")
print(f"API_HASH: {os.environ.get('API_HASH')}")
print(f"LOG_CHANNEL_ID from env: {os.environ.get('LOG_CHANNEL_ID')}")

def get_env_var_as_int(var_name: str, default: int = 0) -> int:
    """Retrieve an environment variable as an integer."""
    value = os.environ.get(var_name, default)
    if value == "":
        raise ValueError(f"{var_name} must be set in the environment variables.")
    if not str(value).isdigit():
        raise ValueError(f"{var_name} must be a number, got '{value}' instead.")
    return int(value)

# Retrieve and validate environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in the environment variables.")

BOT_WORKERS = get_env_var_as_int("BOT_WORKERS", 4)
APP_ID = get_env_var_as_int("APP_ID")
API_HASH = os.environ.get("API_HASH", "")
if not API_HASH:
    raise ValueError("API_HASH must be set in the environment variables.")

LOG_CHANNEL_ID = get_env_var_as_int("LOG_CHANNEL_ID")

MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "izzyganteng")
BROADCAST_AS_COPY = True

PLUG = dict(root="antigcast/plugins")

OWNER_ID = [int(x) for x in (os.environ.get("OWNER_ID", "").split()) if x.isdigit()]
OWNER_NAME = os.environ.get("OWNER_NAME", "")

# Configure logging
LOG_FILE_NAME = "antigcast_logs.txt"
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50000000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
