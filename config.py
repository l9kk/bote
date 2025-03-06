import os
import sys
import json

print("===== ATTEMPTING TO LOAD BOT CONFIGURATION =====")

# Try multiple methods to get the token
bot_token = None

# Method 1: Direct environment variable
if not bot_token:
    bot_token = os.environ.get("BOT_TOKEN")
    if bot_token:
        print("Found BOT_TOKEN via direct environment variable")

# Method 2: Alternative environment variable names
if not bot_token:
    for name in ["bot_token", "TELEGRAM_TOKEN", "telegram_token", "TOKEN", "BOTTOKEN"]:
        if name in os.environ:
            bot_token = os.environ[name]
            print(f"Found token via alternative name: {name}")
            break

# Method 3: Railway specific configuration
if not bot_token and "RAILWAY_SERVICE_NAME" in os.environ:
    try:
        with open("/railway/config.json", "r") as f:
            config = json.load(f)
            if "BOT_TOKEN" in config:
                bot_token = config["BOT_TOKEN"]
                print("Found BOT_TOKEN in Railway config.json")
    except:
        pass

# Final assignment
BOT_TOKEN = bot_token

# Check if we have a token
if not BOT_TOKEN:
    print("⚠️ ERROR: No BOT_TOKEN found using any method!")
    print("Please add BOT_TOKEN to your Railway variables.")
    sys.exit(1)
else:
    print(f"✅ BOT_TOKEN found! ({len(BOT_TOKEN)} chars)")

# OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY:
    print(f"✅ OPENAI_API_KEY found! ({len(OPENAI_API_KEY)} chars)")
else:
    print("⚠️ No OPENAI_API_KEY found - will use local analysis only")

# Optional proxy URL
PROXY_URL = os.environ.get("PROXY_URL", "")

# List of supported music file extensions
MUSIC_EXTENSIONS = {
    ".mp3", ".m4a", ".flac", ".wav", ".ogg", ".opus",
    ".aac", ".wma", ".alac", ".aiff", ".ape"
}