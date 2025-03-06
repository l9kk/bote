import os
import sys
import json
from dotenv import load_dotenv

# First try to load from .env file for local development
load_dotenv()

# Debug information
print("===== ENVIRONMENT VARIABLES DEBUG =====")
print(f"Running in directory: {os.getcwd()}")
print(f"All environment variables: {list(os.environ.keys())}")
print(f"BOT_TOKEN exists: {bool(os.getenv('BOT_TOKEN'))}")
print(f"OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
print("=======================================")

# Try to get variables directly from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_URL = os.getenv("PROXY_URL", "")

# If we're on Railway, try alternative approaches to get variables
if "RAILWAY_SERVICE_NAME" in os.environ:
    print("Detected Railway environment, trying alternative approaches...")

    # Try to read from RAILWAY_VOLUME_MOUNT_PATH if available
    railway_env_path = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "/railway/volume")
    if os.path.isdir(railway_env_path):
        try:
            with open(f"{railway_env_path}/config.json", "r") as f:
                config = json.load(f)
                if not BOT_TOKEN and "BOT_TOKEN" in config:
                    BOT_TOKEN = config["BOT_TOKEN"]
                if not OPENAI_API_KEY and "OPENAI_API_KEY" in config:
                    OPENAI_API_KEY = config["OPENAI_API_KEY"]
                print("Loaded variables from Railway volume mount")
        except Exception as e:
            print(f"Error loading from Railway volume: {e}")

# Check if .env.railway file exists (another approach for Railway)
if os.path.isfile(".env.railway"):
    try:
        with open(".env.railway", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    if key == "BOT_TOKEN" and not BOT_TOKEN:
                        BOT_TOKEN = value
                    elif key == "OPENAI_API_KEY" and not OPENAI_API_KEY:
                        OPENAI_API_KEY = value
        print("Loaded variables from .env.railway file")
    except Exception as e:
        print(f"Error loading from .env.railway: {e}")

# Last resort: Try to create a temporary .env.railway file with instructions
if not BOT_TOKEN:
    try:
        with open(".env.railway", "w") as f:
            f.write("# Add your variables here for Railway\n")
            f.write("BOT_TOKEN=your_bot_token_here\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("Created .env.railway template file - please add your variables")
    except Exception as e:
        print(f"Error creating template: {e}")

# Final check - validate BOT_TOKEN
if not BOT_TOKEN:
    print("\n⚠️  CRITICAL ERROR: BOT_TOKEN is missing! ⚠️")
    print("The bot cannot start without a valid Telegram Bot Token.")
    print("\nPossible solutions:")
    print("1. Make sure BOT_TOKEN is set in Railway variables")
    print("2. If running locally, create a .env file with BOT_TOKEN=your_token")
    print("3. Set it directly in the environment\n")
    print("Example token format: 1234567890:ABCDEF-ghijklmnopqrstuvwxyz\n")
    sys.exit(1)

# Warning for missing OpenAI API key
if not OPENAI_API_KEY:
    print("\n⚠️ WARNING: No OPENAI_API_KEY found. Music analysis will use local fallback only.")

# List of supported music file extensions
MUSIC_EXTENSIONS = {
    ".mp3", ".m4a", ".flac", ".wav", ".ogg", ".opus",
    ".aac", ".wma", ".alac", ".aiff", ".ape"
}