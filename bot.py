import asyncio
import logging
import os
import socket
import sys
import signal
from collections import defaultdict
from typing import Dict, List, Optional

from openai import OpenAI
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ContentType
from aiogram.filters import CommandObject

from config import BOT_TOKEN, OPENAI_API_KEY, MUSIC_EXTENSIONS, PROXY_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Store music files per chat
chat_music_files: Dict[int, List[str]] = {}

# Create a PID file path
PID_FILE = "bot.pid"


def create_pid_file():
    """Create a PID file to prevent multiple instances."""
    # Check if PID file exists
    if os.path.isfile(PID_FILE):
        with open(PID_FILE, 'r') as file:
            old_pid = file.read().strip()

        # Check if process is still running
        try:
            # For Windows
            if sys.platform == 'win32':
                # Use tasklist to check if process exists
                import subprocess
                output = subprocess.check_output(['tasklist', '/FI', f'PID eq {old_pid}']).decode()
                if f"PID {old_pid}" in output or f"PID: {old_pid}" in output:
                    logger.error(f"Another instance of this bot is already running (PID: {old_pid})")
                    print("\n⚠️  INSTANCE CONFLICT ⚠️")
                    print(f"Another bot instance is already running with PID {old_pid}.")
                    print("Please stop that instance before starting a new one.")
                    print("You can:")
                    print("1. Close the other command window running the bot")
                    print("2. Use Task Manager to end the python.exe process")
                    print("3. Or delete the bot.pid file if you're sure no other instance is running\n")
                    sys.exit(1)
            else:
                # For Unix-like systems
                try:
                    os.kill(int(old_pid), 0)
                    logger.error(f"Another instance of this bot is already running (PID: {old_pid})")
                    print("\n⚠️  INSTANCE CONFLICT ⚠️")
                    print(f"Another bot instance is already running with PID {old_pid}.")
                    print("Please stop that instance before starting a new one.")
                    sys.exit(1)
                except OSError:
                    # Process doesn't exist, we can continue
                    pass
        except:
            # If any error occurs, assume the process is not running
            pass

    # Create new PID file
    with open(PID_FILE, 'w') as file:
        file.write(str(os.getpid()))

    # Register cleanup to remove PID file on exit
    def cleanup_pid_file(*args):
        try:
            os.unlink(PID_FILE)
        except:
            pass
        if args:  # If signal handler
            sys.exit(0)

    # Register signals
    signal.signal(signal.SIGINT, cleanup_pid_file)
    signal.signal(signal.SIGTERM, cleanup_pid_file)

    # Register cleanup on normal exit
    import atexit
    atexit.register(cleanup_pid_file)


def get_file_extension(file_name: str) -> str:
    """Get the file extension from a filename."""
    _, ext = os.path.splitext(file_name.lower())
    return ext


from aiogram.client.default import DefaultBotProperties

def create_bot() -> Bot:
    """Create a bot instance with correct default properties."""
    session = None
    if PROXY_URL:
        try:
            import aiohttp_socks
            session = AiohttpSession(proxy=PROXY_URL)
        except ImportError:
            logger.error("aiohttp_socks package is not installed. Run 'pip install aiohttp-socks'")
            sys.exit(1)

    try:
        return Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML"),
            session=session
        )
    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        raise


async def check_connection() -> bool:
    """Check if we have internet connection to Telegram API."""
    try:
        # Try to resolve Telegram API domain
        await asyncio.get_running_loop().getaddrinfo('api.telegram.org', 443)
        return True
    except socket.gaierror:
        return False


# Create PID file to prevent multiple instances
create_pid_file()

# Initialize bot and dispatcher
try:
    bot = create_bot()
    dp = Dispatcher()
except Exception as e:
    logger.critical(f"Failed to initialize bot: {e}")
    sys.exit(1)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle the /start command."""
    await message.answer(
        "👋 Welcome to Music Frequency Bot!\n\n"
        "I can help you track the most popular music in your group.\n\n"
        "Use /collect to start collecting music files from the chat history.\n"
        "Use /help to see all available commands."
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle the /help command."""
    help_text = (
        "🎵 <b>Music Frequency Bot</b> 🎵\n\n"
        "<b>Available commands:</b>\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/collect - Start collecting music files from the chat\n"
        "/status - Check the current collection status\n"
        "/clear - Clear the collected file list\n"
        "/nettest - Test network connectivity\n"
    )
    await message.answer(help_text)


@dp.message(Command("nettest"))
async def cmd_nettest(message: types.Message):
    """Test network connectivity."""
    status_msg = await message.answer("🔄 Testing network connection...")

    # Test connection to Telegram API
    telegram_ok = await check_connection()

    # Test connection to OpenAI API
    openai_ok = False
    try:
        # Initialize OpenAI client according to documentation
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Use a shorter timeout to not wait too long
        test_response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini as requested
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=5
        )
        openai_ok = True
    except Exception as e:
        logger.error(f"OpenAI API test failed: {e}")

    # Format test results
    result = (
        "📡 <b>Network Test Results:</b>\n\n"
        f"Telegram API: {'✅ Connected' if telegram_ok else '❌ Connection Failed'}\n"
        f"OpenAI API: {'✅ Connected' if openai_ok else '❌ Connection Failed'}\n\n"
    )

    # Add proxy status if configured
    if PROXY_URL:
        result += f"<b>Proxy configured:</b> {PROXY_URL}\n\n"

    if not telegram_ok:
        result += (
            "<b>Troubleshooting Telegram connection:</b>\n"
            "• Check your internet connection\n"
            "• Check if a firewall is blocking access\n"
            "• Check DNS settings\n\n"
        )

    if not openai_ok:
        result += (
            "<b>Troubleshooting OpenAI connection:</b>\n"
            "• Verify your API key is correct\n"
            "• Check if your OpenAI account has sufficient credits\n"
            "• Check if your IP is allowed to access OpenAI\n"
        )

    await status_msg.edit_text(result)

@dp.message(F.content_type.in_([ContentType.AUDIO, ContentType.DOCUMENT]))
async def collect_music_from_messages(message: types.Message):
    chat_id = message.chat.id
    chat_music_files.setdefault(chat_id, [])

    file_name = None

    if message.audio:
        file_name = message.audio.file_name or f"{message.audio.performer} - {message.audio.title}"
        chat_music_files[chat_id].append(file_name)
        logger.info(f"Collected audio: {file_name} from chat {chat_id}")

    elif message.document:
        file_name = message.document.file_name
        if get_file_extension(file_name) in MUSIC_EXTENSIONS:
            chat_music_files[chat_id].append(file_name)
            logger.info(f"Collected document: {file_name} from chat {chat_id}")

@dp.message(Command("collect"))
async def cmd_collect(message: types.Message, command: CommandObject):
    target_chat = command.args
    if not target_chat:
        await message.reply(
            "Please specify a chat username or ID:\n"
            "`/collect @chatusername` or `/collect -1001234567890`",
            parse_mode='Markdown'
        )
        return

    # Resolve real chat_id from provided username or ID
    try:
        target_chat_obj = await bot.get_chat(target_chat)
        target_chat_id = target_chat_obj.id
    except Exception as e:
        logger.error(f"Failed to resolve chat_id: {e}")
        await message.answer("❌ Could not find the specified chat. Check permissions and access.")
        return

    # Check if music files already collected for the specified chat
    count = len(chat_music_files.get(target_chat_id, []))
    if count == 0:
        await message.answer("❌ No music collected yet for this chat. Please send or forward music files there so the bot can start collecting them.")
        return

    # Create the Analyze button
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text=f"📊 Analyze {count} Music Files",
        callback_data=f"analyze_music:{target_chat_id}"
    ))

    await message.answer(
        f"✅ Found {count} music files in chat {target_chat}.",
        reply_markup=keyboard.as_markup()
    )

@dp.callback_query(F.data.startswith("analyze_music"))
async def analyze_music_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id

    # Check if any music files collected for this chat
    if not chat_music_files.get(chat_id):
        await callback.message.edit_text("❌ No music to analyze. Please use /collect first.")
        await callback.answer()
        return

    await callback.message.edit_text("🧠 Analyzing music... Please wait...")

    music_count = defaultdict(int)
    for file_name in chat_music_files[chat_id]:
        music_count[file_name] += 1

    response = await local_analyze_music(music_count)

    await callback.message.answer(response)
    await callback.answer()


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    """Show the current collection status."""
    chat_id = message.chat.id

    if not chat_id in chat_music_files or not chat_music_files[chat_id]:
        await message.answer("No music files collected yet. Use /collect to start.")
        return

    unique_count = len(set(chat_music_files[chat_id]))
    total_count = len(chat_music_files[chat_id])

    # Create analyze button
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text=f"📊 Analyze {total_count} Music Files",
        callback_data="analyze_music"
    ))

    await message.answer(
        f"📑 Collection Status:\n"
        f"Total music files: {total_count}\n"
        f"Unique music files: {unique_count}",
        reply_markup=keyboard.as_markup()
    )


@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    """Clear the collected file list."""
    chat_id = message.chat.id

    if chat_id in chat_music_files:
        del chat_music_files[chat_id]

    await message.answer("🧹 Music file collection has been cleared.")


async def analyze_with_openai(music_list: str) -> Optional[str]:
    """Analyze music list using OpenAI API with gpt-4o-mini model."""
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not set")
        return None

    try:
        # Initialize OpenAI client according to documentation
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini as requested
            messages=[
                {"role": "system",
                 "content": "You are a music analysis assistant. Sort the provided list by frequency and provide insights about the most popular music."},
                {"role": "user",
                 "content": f"Sort this list of music by frequency and provide a concise analysis:\n\n{music_list}"}
            ],
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None


async def local_analyze_music(music_count: Dict[str, int]) -> str:
    """Fallback analyzer when OpenAI is not available."""
    sorted_music = sorted(
        music_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Generate analysis text
    result = "<b>🎵 Music Frequency Analysis</b>\n\n"
    result += "<b>Most Popular Tracks:</b>\n"

    for i, (track, count) in enumerate(sorted_music[:20], 1):
        result += f"{i}. {track} - <b>{count} plays</b>\n"

    if len(sorted_music) > 20:
        result += f"\n<i>...and {len(sorted_music) - 20} more tracks</i>\n"

    result += f"\n<b>Total:</b> {len(sorted_music)} unique tracks found"

    return result


async def main():
    """Start the bot with proper connection handling."""
    try:
        # Check connection
        if not await check_connection():
            logger.error("No connection to Telegram API. Please check your internet or proxy settings.")
            print("\n⚠️  CONNECTION ERROR ⚠️")
            print("Cannot connect to Telegram API. Possible solutions:")
            print("1. Check your internet connection")
            print("2. Configure a proxy in config.py if you're in a region with restricted access")
            print("3. Check if your firewall is blocking the connection")
            print("4. Check your DNS settings\n")
            return

        logger.info("Bot is starting...")
        # Skip pending updates and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
    finally:
        # Graceful shutdown
        logger.info("Bot is shutting down")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")