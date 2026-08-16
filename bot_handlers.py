"""
bot_handlers.py
----------------
Contains the logic that reacts to incoming Rubika messages.

`register_handlers(client)` attaches an update listener to the given
rubpy BotClient. Whenever a new text message arrives, it is forwarded to
the AI (via ai_handler.get_ai_response) and the reply is sent back to
the same chat.

This follows rubpy's officially documented Bot API pattern:

    from rubpy.bot import BotClient, filters

    app = BotClient("bot_token")

    @app.on_update(filters.text)
    async def handler(client, message):
        await message.reply("...")

    app.run()

i.e. the handler receives the `message` object directly and replies via
`message.reply(...)` — there is no separate "Update" wrapper object to
import, and no "models.Update" type (that type does not exist in rubpy's
public API and importing it will raise ImportError).
"""

from rubpy.bot import filters

from ai_handler import get_ai_response
from config import IGNORED_CHAT_GUIDS


def register_handlers(client) -> None:
    """
    Register all Rubika update handlers on the given BotClient.
    Call this once, before client.run().
    """

    # filters.text -> only fires for updates that contain a text message.
    # (Add filters.private here too if you want the bot to reply only in
    #  direct/private chats and stay silent in groups, e.g.:
    #  @client.on_update(filters.text, filters.private))
    @client.on_update(filters.text)
    async def handle_new_message(_client, message):
        """
        Fired for every new text message update the bot receives.

        `message` is rubpy's Message object. Field names are accessed
        defensively with getattr(...) because rubpy's public API has
        changed field names between versions in the past — this keeps
        the bot working across minor version bumps instead of raising
        an AttributeError.
        """
        try:
            text = getattr(message, "text", None)
            if not text:
                return

            # Bot API updates are essentially always from real users
            # talking to the bot, but skip anything that looks like it
            # came from another bot, just in case (avoids bot-to-bot
            # reply loops).
            sender_type = getattr(message, "sender_type", None)
            if sender_type and "bot" in str(sender_type).lower():
                return

            # Ignore chats explicitly listed in config.IGNORED_CHAT_GUIDS.
            chat_id = getattr(message, "chat_id", None) or getattr(message, "object_guid", None)
            if chat_id and chat_id in IGNORED_CHAT_GUIDS:
                return

            # --- Get AI reply ---------------------------------------------

            ai_reply = await get_ai_response(text)

            # --- Send the reply back to the same chat ----------------------

            await message.reply(ai_reply)

        except Exception as e:
            # Never let a single bad update crash the whole bot.
            print(f"[bot_handlers] Error while handling update: {e}")
