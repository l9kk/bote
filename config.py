import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot token from BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Optional proxy URL for regions with restricted access
PROXY_URL = os.getenv("PROXY_URL", "")

# List of supported music file extensions
MUSIC_EXTENSIONS = {
    ".mp3", ".m4a", ".flac", ".wav", ".ogg", ".opus",
    ".aac", ".wma", ".alac", ".aiff", ".ape"
}