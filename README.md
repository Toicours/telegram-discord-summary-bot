# Telegram to Discord Summary Bot

This bot automatically summarizes content from a Telegram channel and posts the summaries to a Discord channel using AI.

## Features

- Monitors a specified Telegram channel for messages
- Generates daily summaries using AI (DeepSeek or Claude)
- Posts formatted summaries to a Discord channel
- Configurable scheduling
- Modular architecture for easy maintenance

## Setup

### Prerequisites

- Python 3.8 or higher
- Telegram API credentials
- Discord bot token
- AI API key (DeepSeek or Anthropic)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the `.env` file with your credentials (see `.env` section below)

### Configuration

Create a `.env` file in the project root with the following properties:

```
# Telegram API credentials
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=+1234567890
TELEGRAM_SOURCE_CHANNEL=@channel_name

# Discord configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_DESTINATION_CHANNEL_ID=123456789

# LLM Provider (options: 'deepseek' or 'anthropic')
LLM_PROVIDER=deepseek
LLM_API_KEY=your_api_key_here

# Time for daily summary (24-hour format)
SUMMARY_HOUR=23
SUMMARY_MINUTE=0
```

## Usage

Run the application:

```bash
python main.py
```

On first run, Telegram will send an authentication code to your account. Enter this code in the console when prompted.

## How It Works

1. The bot authenticates with Telegram using your account
2. When scheduled, it collects messages from the specified Telegram channel
3. The collected messages are sent to an AI service for summarization
4. The summary is posted to the configured Discord channel

## Project Structure

- `main.py` - Main application entry point
- `config.py` - Configuration management
- `summarizers/` - AI summarization components
- `clients/` - Telegram and Discord client implementations
- `utils/` - Helper utilities

## Troubleshooting

Check the `telegram_to_discord_bot.log` file for detailed logging information if you encounter issues.

## License

MIT
