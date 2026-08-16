"""
config.py
---------
All settings for the bot live here.

This file reads sensitive values from ENVIRONMENT VARIABLES FIRST
(so it works cleanly on Railway or any other host), and falls back
to the literal values below for local testing.

>>> FOR LOCAL TESTING: paste your keys directly into the fallback
    strings below, OR (recommended) create a ".env" file — see
    ".env.example" — and they'll be picked up automatically.
>>> FOR RAILWAY / PRODUCTION: set OPENROUTER_API_KEY and
    RUBIKA_BOT_TOKEN as environment variables in the Railway
    dashboard. Never hardcode real secrets in this file if the
    project is pushed to a public GitHub repo.
"""

import os

# Load a local .env file if python-dotenv is installed and a .env
# file exists. This is only for local development — Railway (and
# most hosts) inject environment variables directly, so this is a
# no-op there.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional; if it's not installed we simply
    # rely on real environment variables (e.g. set by Railway).
    pass


# =========================================================
# 1) OPENROUTER SETTINGS
# =========================================================

# Reads from the OPENROUTER_API_KEY environment variable first.
# If it's not set, falls back to the placeholder string below —
# replace the placeholder ONLY for local testing on your own machine.
OPENROUTER_API_KEY = os.getenv("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")

# The AI model to use. You can change this later to any model
# supported by OpenRouter (e.g. "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", etc.)
# Reads from DEFAULT_MODEL env var first, otherwise uses this free model.
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "meta-llama/llama-3.1-8b-instruct")

# OpenRouter API endpoint (official, no need to change this).
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Optional but recommended by OpenRouter: identify your app.
# You can leave these as-is or customize them.
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://example.com")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Rubika AI Bot")

# System prompt that defines how the AI should behave.
# Feel free to edit this to change the bot's personality.
SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant replying to messages "
    "inside a Rubika messenger chat. Keep answers clear and concise."
)

# Max tokens for the AI reply (adjust if you want longer/shorter answers).
MAX_TOKENS = 1024

# Temperature controls creativity (0.0 = very focused, 1.0 = very creative).
TEMPERATURE = 0.7


# =========================================================
# 2) RUBIKA BOT SETTINGS
# =========================================================

# Your Rubika Bot Token, obtained from @BotFather on Rubika.
# Reads from the RUBIKA_BOT_TOKEN environment variable first.
# If it's not set, falls back to the placeholder string below —
# replace the placeholder ONLY for local testing on your own machine.
#
# The bot connects using this token directly — there is no
# interactive session login, no QR code, and nothing else to
# configure. This makes the bot suitable for 24/7 unattended
# hosting (e.g. Railway).
RUBIKA_BOT_TOKEN = os.getenv("DGFDB0BTHBAALETZCWYCYTIEBGVZZLXUHQFHTKKZMXTPPZNGWWYGARMOYRTXLPGN")

# If you want the bot to ignore messages from certain chat IDs
# (for example, to avoid replying in specific groups), add them here.
IGNORED_CHAT_GUIDS = []
