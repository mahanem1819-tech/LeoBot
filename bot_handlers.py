"""
bot_handlers.py
----------------
Contains the logic that reacts to incoming Rubika messages.

`register_handlers(client)` attaches an update listener to the given
rubpy BotClient. Whenever a new text message arrives, it is forwarded
to the AI (via ai_handler.get_ai_response) and the reply is sent back
to the same chat.

This uses rubpy's Bot API (rubpy.bot.BotClient), which authenticates
with a Bot Token — no interactive session login involved.
"""

from rubpy.bot import filters
from rubpy.bot.models import Update

from ai_handler import get_ai_response
from config import IGNORED_CHAT_GUIDS


def register_handlers(client) -> None:
    """
    Register all Rubika update handlers on the given BotClient.
    Call this once, before client.run().
    """

    # filters.text -> only fires for updates that contain a text message.
    # (Add filters.private here too if you want the bot to reply only
    #  in direct/private chats and stay silent in groups, e.g.:
    #  @client.on_update(filters.text, filters.private))
    @client.on_update(filters.text)
    async def handle_new_message(bot, update: Update):
        """
        Fired for every new text message update the bot receives.
        """
        try:
            message = update.new_message
            if not message or not message.text:
                return

            # Bot API updates are essentially always from real users
            # talking to the bot, but skip anything sent by another
            # bot just in case (avoids bot-to-bot reply loops).
            if message.sender_type and str(message.sender_type).lower() == "bot":
                return

            # Ignore chats explicitly listed in config.IGNORED_CHAT_GUIDS.
            chat_id = update.chat_id
            if chat_id in IGNORED_CHAT_GUIDS:
                return

            # --- Get AI reply ---------------------------------------------------

            ai_reply = await get_ai_response(message.text)

            # --- Send the reply back to the same chat ---------------------------

            await update.reply(ai_reply)

        except Exception as e:
            # Never let a single bad update crash the whole bot.
            print(f"[bot_handlers] Error while handling update: {e}")
