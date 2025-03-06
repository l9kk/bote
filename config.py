import os
import sys

# Delete any existing .env.railway file
try:
    if os.path.exists(".env.railway"):
        os.remove(".env.railway")
        print("Deleted .env.railway file")
except Exception as e:
    print(f"Could not delete .env.railway: {e}")

# Bot token from BotFather (required)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("⚠️ ERROR: No BOT_TOKEN found!")
    sys.exit(1)

# OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Optional proxy URL
PROXY_URL = os.environ.get("PROXY_URL", "")

# List of supported music file extensions
MUSIC_EXTENSIONS = {
    ".mp3", ".m4a", ".flac", ".wav", ".ogg", ".opus",
    ".aac", ".wma", ".alac", ".aiff", ".ape"
}