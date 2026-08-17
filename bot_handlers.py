from rubpy.bot import filters

from ai_handler import get_ai_response
from config import IGNORED_CHAT_GUIDS


def register_handlers(client) -> None:

    @client.on_update(filters.text)
    async def handle_new_message(_client, update):
        try:
            # Rubpy sends an Update object.
            # The actual incoming message is inside update.new_message.
            message = getattr(update, "new_message", None)

            if message is None:
                return

            text = getattr(message, "text", None)

            if not text:
                return

            # Ignore messages sent by bots.
            sender_type = getattr(message, "sender_type", None)

            if sender_type and "bot" in str(sender_type).lower():
                return

            # Get the chat ID from the Update object.
            chat_id = getattr(update, "chat_id", None)

            if chat_id and chat_id in IGNORED_CHAT_GUIDS:
                return

            print(f"📩 New message received: {text[:50]}")

            # Ask OpenRouter for a response.
            ai_reply = await get_ai_response(
    text,
    user_id=getattr(update, "author_guid", None) or getattr(update, "sender_guid", None),
    chat_id=chat_guid,
)

            print("🤖 AI response generated.")

            # Update.reply() sends the response to the same chat.
            await update.reply(ai_reply)

            print("✅ Reply sent.")

        except Exception as e:
            print(f"❌ Error while handling update: {e}")
