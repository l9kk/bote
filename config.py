import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
# This won't affect Railway which sets variables directly
load_dotenv()

# Print environment variable debugging info (temporary, remove in production)
print("Environment Variables Debug:")
print(f"BOT_TOKEN exists: {bool(os.getenv('BOT_TOKEN'))}")
print(f"OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")

# Bot token from BotFather (required)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("⚠️ ERROR: No BOT_TOKEN found in environment variables!")
    print("Make sure to set the BOT_TOKEN environment variable in Railway.")
    sys.exit(1)

# OpenAI API key (optional for this bot since we have a fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️ WARNING: No OPENAI_API_KEY found. Will use local analysis only.")

# Optional proxy URL for regions with restricted access
PROXY_URL = os.getenv("PROXY_URL", "")

# List of supported music file extensions
MUSIC_EXTENSIONS = {
    ".mp3", ".m4a", ".flac", ".wav", ".ogg", ".opus",
    ".aac", ".wma", ".alac", ".aiff", ".ape"
}