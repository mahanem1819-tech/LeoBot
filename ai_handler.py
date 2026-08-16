"""
ai_handler.py
-------------
Handles all communication with the OpenRouter API.

This module exposes a single async function, `get_ai_response`, which
takes a user's text message and returns the AI's reply as a string.
"""

import httpx

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    OPENROUTER_SITE_URL,
    OPENROUTER_APP_NAME,
    DEFAULT_MODEL,
    SYSTEM_PROMPT,
    MAX_TOKENS,
    TEMPERATURE,
)


async def get_ai_response(user_message: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send `user_message` to OpenRouter and return the AI's text reply.

    Args:
        user_message: The text the user sent on Rubika.
        model: Which OpenRouter model to use (defaults to config.DEFAULT_MODEL).

    Returns:
        The AI's reply as a string. If something goes wrong, a friendly
        error message is returned instead of raising, so the bot never
        crashes because of a bad API response.
    """

    # Basic safety check before even calling the API.
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "PUT_YOUR_OPENROUTER_API_KEY_HERE":
        return (
            "⚠️ OpenRouter API key is not set. "
            "Please put your key in config.py -> OPENROUTER_API_KEY."
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # These two headers are optional but recommended by OpenRouter.
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": OPENROUTER_APP_NAME,
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)

        # Raise an exception for HTTP error status codes (4xx, 5xx).
        response.raise_for_status()

        data = response.json()

        # Defensive parsing: make sure the expected fields exist.
        choices = data.get("choices")
        if not choices:
            return "⚠️ The AI service returned an unexpected response (no choices)."

        message = choices[0].get("message", {})
        content = message.get("content")

        if not content:
            return "⚠️ The AI service returned an empty reply."

        return content.strip()

    except httpx.TimeoutException:
        return "⚠️ The AI service took too long to respond. Please try again."

    except httpx.HTTPStatusError as e:
        # Try to extract a useful error message from OpenRouter's response.
        try:
            error_info = e.response.json()
            error_msg = error_info.get("error", {}).get("message", str(e))
        except Exception:
            error_msg = str(e)
        return f"⚠️ AI service error ({e.response.status_code}): {error_msg}"

    except httpx.RequestError as e:
        return f"⚠️ Network error while contacting the AI service: {e}"

    except Exception as e:
        # Catch-all so the bot never crashes because of an unexpected issue.
        return f"⚠️ Unexpected error in AI handler: {e}"
