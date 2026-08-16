"""
config.py
---------
All settings for the bot live here.

PRODUCTION (Railway, or any real deployment):
    Set these as real environment variables in your host's dashboard.
    Required:
        RUBIKA_BOT_TOKEN     -> your Rubika bot token
        OPENROUTER_API_KEY   -> your OpenRouter API key
    Optional:
        DEFAULT_MODEL        -> defaults to "meta-llama/llama-3.1-8b-instruct"
    Nothing else needs to be edited in this file for production use.

LOCAL DEVELOPMENT:
    Copy ".env.example" to ".env" and fill in real values there. This file
    is loaded automatically (see below) — real, already-set environment
    variables (like the ones Railway injects) always take priority over
    anything in ".env", and this file never writes secrets back to disk.

This module does NOT hardcode any real secret and does NOT silently fall
back to a placeholder value for required settings — if a required
variable is missing, `validate_config()` (called from main.py before the
bot starts) raises a clear error that names the missing variable without
ever printing its value.
"""

import os

# ---------------------------------------------------------------------------
# Local-only .env loading
# ---------------------------------------------------------------------------
# `override=False` is the python-dotenv default, but it's set explicitly
# here for clarity: if a variable is already present in the real process
# environment (as it always is on Railway, since Railway injects variables
# directly into the container's environment before Python even starts),
# that real value is kept and ".env" is NOT allowed to overwrite it.
# On a host with no ".env" file at all (e.g. Railway), this is a silent,
# harmless no-op — production never depends on this file existing.
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    # python-dotenv is only needed for local convenience; if it isn't
    # installed we simply rely on real environment variables.
    pass


def _clean(value):
    """Treat an empty/whitespace-only env var the same as "not set"."""
    if value is None:
        return None
    value = value.strip()
    return value or None


# =========================================================
# 1) RUBIKA BOT SETTINGS
# =========================================================

# Your Rubika Bot Token. Read ONLY from the RUBIKA_BOT_TOKEN environment
# variable — there is no placeholder fallback, so a missing token is
# caught explicitly by validate_config() instead of failing later with a
# confusing error from inside the Rubika client.
RUBIKA_BOT_TOKEN = _clean(os.environ.get("RUBIKA_BOT_TOKEN"))

# The bot authenticates directly with this token — no interactive login,
# no QR code, no session file. This is what makes it suitable for 24/7
# unattended hosting on Railway.
IGNORED_CHAT_GUIDS = []


# =========================================================
# 2) OPENROUTER SETTINGS
# =========================================================

# Read ONLY from the OPENROUTER_API_KEY environment variable.
OPENROUTER_API_KEY = _clean(os.environ.get("OPENROUTER_API_KEY"))

# The AI model to use. Optional — has a sensible free-tier default so the
# bot works out of the box even if DEFAULT_MODEL isn't set. Override it
# with any model ID supported by OpenRouter (https://openrouter.ai/models).
DEFAULT_MODEL = _clean(os.environ.get("DEFAULT_MODEL")) or "meta-llama/llama-3.1-8b-instruct"

# OpenRouter API endpoint (official, no need to change this).
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Optional but recommended by OpenRouter: identify your app.
OPENROUTER_SITE_URL = _clean(os.environ.get("OPENROUTER_SITE_URL")) or "https://example.com"
OPENROUTER_APP_NAME = _clean(os.environ.get("OPENROUTER_APP_NAME")) or "Rubika AI Bot"

# System prompt that defines how the AI should behave.
SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant replying to messages "
    "inside a Rubika messenger chat. Keep answers clear and concise."
)

# Max tokens for the AI reply.
MAX_TOKENS = 1024

# Temperature controls creativity (0.0 = very focused, 1.0 = very creative).
TEMPERATURE = 0.7


# =========================================================
# 3) STARTUP VALIDATION
# =========================================================

# Every entry here is (env_var_name, human_readable_value).
_REQUIRED_SETTINGS = (
    ("RUBIKA_BOT_TOKEN", RUBIKA_BOT_TOKEN),
    ("OPENROUTER_API_KEY", OPENROUTER_API_KEY),
)


def validate_config() -> None:
    """
    Raise a clear, secret-free error if any required environment variable
    is missing. Call this once, at startup, before creating any client.

    This never prints or includes the *value* of a variable — only its
    *name* — so secrets can never leak into logs through this check.
    """
    missing = [name for name, value in _REQUIRED_SETTINGS if not value]
    if missing:
        missing_list = ", ".join(missing)
        raise RuntimeError(
            "Missing required environment variable(s): "
            f"{missing_list}.\n"
            "Set them in your host's environment (e.g. Railway → your "
            "service → Variables tab) or, for local development, in a "
            "\".env\" file (see .env.example). The app will not start "
            "until these are set."
        )
