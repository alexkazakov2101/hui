# Telegram Bot Tester

This repository contains a minimal prototype for automated testing of a Telegram bot using a large language model (Google Gemini) as the tester.

## Files
- `bot_tester.py` – script that connects to Telegram via Telethon, delegates message generation and analysis to Gemini and walks through a test scenario.
- `scenario.txt` – example scenario used by the script.

## Usage
1. Install requirements:
   ```bash
   pip install telethon google-generativeai
   ```
2. Set the following environment variables:
   - `TG_API_ID` and `TG_API_HASH` – Telegram API credentials from <https://my.telegram.org>.
   - `TG_BOT_USERNAME` – username of the bot to test (without `@`).
   - `GEMINI_API_KEY` – your Google Gemini API key.
3. Optionally edit `scenario.txt` to describe the desired test scenario.
4. Run the tester:
   ```bash
   python bot_tester.py
   ```

This proof-of-concept demonstrates how an external LLM can drive conversations with a Telegram bot and provide feedback for improvement.
