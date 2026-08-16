"""
main.py
-------
Entry point for the Rubika AI bot.

Run this file to start the bot:
    python main.py

The bot authenticates using a Rubika BOT TOKEN (config.RUBIKA_BOT_TOKEN /
the RUBIKA_BOT_TOKEN environment variable) — there is no interactive
login step, no QR code, and no session file. This means the bot can
run unattended 24/7 on any host (e.g. Railway) as soon as the token
and API key environment variables are set.
"""

import asyncio

from rubpy.bot import BotClient

from config import RUBIKA_BOT_TOKEN
from bot_handlers import register_handlers


async def main():
    if not RUBIKA_BOT_TOKEN or RUBIKA_BOT_TOKEN == "PUT_YOUR_RUBIKA_BOT_TOKEN_HERE":
        print(
            "❌ RUBIKA_BOT_TOKEN is not set.\n"
            "   Set it as an environment variable, or put it in config.py "
            "for local testing."
        )
        return

    # Create the Rubika bot client using the bot token.
    client = BotClient(RUBIKA_BOT_TOKEN)

    # Attach all message handlers defined in bot_handlers.py.
    register_handlers(client)

    print("🤖 Rubika AI Bot is starting...")

    # client.run() starts the bot (long-polling by default) and keeps
    # it running until stopped. No login prompt — the bot token is
    # all that's needed.
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user.")
    except Exception as e:
        print(f"❌ Bot crashed with an unexpected error: {e}")
