"""
main.py
-------
Entry point for the Rubika AI bot.

Run this file to start the bot:
    python main.py

The bot authenticates using a Rubika BOT TOKEN (RUBIKA_BOT_TOKEN env var)
— there is no interactive login step, no QR code, and no session file.
This means the bot can run unattended 24/7 on any host (e.g. Railway) as
soon as the required environment variables are set.

Note on rubpy's event loop: rubpy's BotClient manages its own asyncio
event loop internally. Its documented usage is a *plain, synchronous*
call to `client.run()` — it is NOT awaited and NOT wrapped in
`asyncio.run(...)`. Wrapping it in an extra asyncio.run() call (as an
earlier version of this file did) fights with rubpy's internal loop and
can prevent the bot from starting cleanly. This file follows rubpy's
documented pattern exactly.
"""

import sys

from rubpy.bot import BotClient

from config import RUBIKA_BOT_TOKEN, validate_config
from bot_handlers import register_handlers


def main() -> None:
    # Fail loudly and immediately if required environment variables are
    # missing, instead of printing a message and exiting with code 0.
    # A silent, "successful" exit is what causes a worker process on
    # Railway to just quietly stop (and get endlessly restarted) without
    # ever surfacing as an obvious crash in the deploy status — raising
    # here makes the failure unambiguous in the Railway logs.
    validate_config()

    # Create the Rubika bot client using the bot token.
    client = BotClient(RUBIKA_BOT_TOKEN)

    # Attach all message handlers defined in bot_handlers.py.
    register_handlers(client)

    print("🤖 Rubika AI Bot is starting...")

    # client.run() is a blocking call that starts the bot (long-polling)
    # and keeps it running until the process is stopped. This matches
    # rubpy's documented usage exactly — no login prompt, no extra
    # asyncio wrapper needed.
    client.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user.")
        sys.exit(0)
    except RuntimeError as e:
        # Raised by config.validate_config() for missing env vars, or by
        # rubpy itself for an invalid/rejected token. Printed to stderr
        # (visible in Railway's logs) with a non-zero exit code so the
        # failure is unmistakable instead of looking like a clean stop.
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Bot crashed with an unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
