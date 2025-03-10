# Music Frequency Bot for Telegram

A Telegram bot that tracks and analyzes the most frequently shared music in your chats. This bot identifies music by metadata rather than just filenames, providing accurate statistics on your group's musical preferences.


## Features

- 🎵 Automatically collects music files shared in your Telegram chats
- 🎧 Identifies music by metadata (artist, title) rather than just filenames
- 📊 Analyzes and lists the most popular tracks in your chats
- 🌐 Works in private chats, groups, and channels
- 🔄 Simple commands for easy interaction

## Installation

### Prerequisites

- Python 3.7 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/music-frequency-bot.git
   cd music-frequency-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a configuration file:
   ```bash
   cp config.example.py config.py
   ```

4. Edit `config.py` with your bot token and other settings:
   ```python
   BOT_TOKEN = "your_bot_token_here"
   MUSIC_EXTENSIONS = [".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac"]
   PROXY_URL = None  # Set if needed
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

- `BOT_TOKEN`: Your Telegram Bot token (required)
- `MUSIC_EXTENSIONS`: List of file extensions to recognize as music files
- `PROXY_URL`: Proxy URL if you need to connect through a proxy

## Usage

### Bot Commands

- `/start` - Start the bot and get a welcome message
- `/help` - Display available commands and their descriptions
- `/collect` - Start collecting music files from the current chat
- `/status` - Check how many music files have been collected so far
- `/clear` - Clear the collected music files for the current chat
- `/nettest` - Test network connectivity to Telegram API

### Basic Usage

1. Add the bot to your group chat
2. Give it permission to read messages
3. Users share music files in the group
4. Type `/collect` to analyze the most frequently shared music
5. View the analysis results

## How It Works

The bot collects audio files shared in your Telegram chats. For each audio file, it:

1. Extracts the performer and title from audio metadata
2. Falls back to file name if metadata is unavailable
3. Tracks the frequency of each unique track
4. When requested, lists the most popular music files

## Example

After several music files have been shared in a chat:

```
User: /collect
Bot: ✅ Found 42 music files in Music Lovers Group.
     [📊 Analyze 42 Music Files]

User: *clicks the analyze button*
Bot: 🧠 Analyzing music... Please wait...

🎵 Music Frequency Analysis

Most Popular Tracks:
1. Shakira - Waka Waka - 15 plays
2. The Weeknd - Blinding Lights - 9 plays  
3. Dua Lipa - Levitating - 7 plays
4. BTS - Dynamite - 5 plays
5. Lady Gaga - Bad Romance - 3 plays
...

Total: 23 unique tracks found
```

## Technical Details

- Built with [aiogram](https://github.com/aiogram/aiogram) framework
- Uses Telegram's audio file metadata for accurate music identification
- Optional OpenAI integration for more detailed music trend analysis
- Multi-chat support: tracks music separately for each chat

## Troubleshooting

- **Bot doesn't respond**: Ensure the bot has been added to the chat and has permission to read messages
- **No music collected**: Make sure music files are being shared in the correct format (audio files)
- **Network issues**: Use `/nettest` to diagnose connection problems
- **Multiple instances warning**: Only run one instance of the bot at a time

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
