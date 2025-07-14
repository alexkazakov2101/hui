"""Telegram bot tester using Telethon and Gemini LLM.

This script connects to Telegram as a user via Telethon and interacts with a
specified bot. It delegates message generation and analysis to a Gemini LLM via
the google-generativeai package.

Prerequisites:
- Set the environment variables TG_API_ID, TG_API_HASH for Telegram API.
- Set GEMINI_API_KEY with your Gemini access token.
- Set TG_BOT_USERNAME with the target bot's username (without @).
- Prepare a scenario in scenario.txt describing the test goals.

This script is a minimal demonstration and omits robust error handling.
"""
import asyncio
import os

from telethon import TelegramClient
import google.generativeai as genai


API_ID = int(os.environ.get("TG_API_ID", 0))
API_HASH = os.environ.get("TG_API_HASH")
BOT_USERNAME = os.environ.get("TG_BOT_USERNAME")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SESSION_NAME = os.environ.get("TG_SESSION", "bot_test")
MAX_STEPS = int(os.environ.get("TEST_STEPS", 5))
SCENARIO_PATH = os.environ.get("TEST_SCENARIO", "scenario.txt")


async def main() -> None:
    if not all([API_ID, API_HASH, BOT_USERNAME, GEMINI_API_KEY]):
        raise RuntimeError("Missing configuration: ensure TG_API_ID, TG_API_HASH, TG_BOT_USERNAME and GEMINI_API_KEY are set")

    scenario = open(SCENARIO_PATH, "r", encoding="utf-8").read().strip()

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")
    convo = model.start_chat(history=[])

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        bot = await client.get_entity(BOT_USERNAME)
        step_prompt = (
            "Ты тестировщик Telegram-бота. Следуй этому сценарию:\n" + scenario +
            "\nСгенерируй первую реплику пользователя."
        )
        user_message = convo.send_message(step_prompt).text
        last_id = 0

        for _ in range(MAX_STEPS):
            await client.send_message(bot, user_message)
            # Ждем нового сообщения от бота
            bot_message = None
            for _ in range(30):
                msgs = await client.get_messages(bot, limit=1)
                if msgs and msgs[0].id != last_id:
                    bot_message = msgs[0]
                    last_id = bot_message.id
                    break
                await asyncio.sleep(1)
            if bot_message is None:
                print("Бот не ответил вовремя. Тест прерван.")
                break
            print(f"Бот: {bot_message.text}")
            # Передаем ответ бота в LLM и получаем следующую реплику и краткий отзыв
            llm_prompt = (
                f"Пользователь сказал: {user_message}\n" +
                f"Бот ответил: {bot_message.text}\n" +
                "Что пользователь скажет дальше? Также перечисли краткие замечания к ответу бота."
            )
            response = convo.send_message(llm_prompt)
            user_message = response.text
            print(f"LLM: {user_message}\n")

        print("\nДиалог завершен. История:")
        for part in convo.history:
            role = part["role"]
            content = part["parts"][0].text if part["parts"] else ""
            print(f"{role.upper()}: {content}")


if __name__ == "__main__":
    asyncio.run(main())
