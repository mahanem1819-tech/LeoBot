from rubpy.bot import filters

from ai_handler import get_ai_response
from config import IGNORED_CHAT_GUIDS


def register_handlers(client) -> None:

    @client.on_update(filters.text)
    async def handle_new_message(_client, update):
        try:
            # Get the actual Rubika message
            message = getattr(update, "new_message", None)

            if message is None:
                print("⚠️ No new_message found in update.")
                return

            # Get text
            text = getattr(message, "text", None)

            if not text:
                return

            # Ignore bot messages
            sender_type = getattr(message, "sender_type", None)

            if sender_type and "bot" in str(sender_type).lower():
                return

            # Get chat ID
            chat_id = (
                getattr(update, "chat_id", None)
                or getattr(message, "chat_id", None)
                or getattr(message, "object_guid", None)
            )

            # Ignore configured chats
            if chat_id and chat_id in IGNORED_CHAT_GUIDS:
                return

            # Get user/sender ID
            user_id = (
                getattr(message, "author_guid", None)
                or getattr(message, "sender_guid", None)
                or getattr(message, "from_guid", None)
                or getattr(update, "author_guid", None)
                or getattr(update, "sender_guid", None)
                or getattr(update, "from_guid", None)
            )

            # Last-resort fallback
            if not user_id:
                user_id = chat_id or "unknown_user"

            print(
                f"📩 New message received: "
                f"user={user_id} chat={chat_id} text={text[:80]}"
            )

            # Ask LeoAI
            ai_reply = await get_ai_response(
                text,
                user_id=str(user_id),
                chat_id=str(chat_id) if chat_id else None,
            )

            print("🤖 AI response generated.")

            # Reply to the same Rubika chat
            await update.reply(ai_reply)

            print("✅ Reply sent.")

        except Exception as e:
            print(f"❌ Error while handling update: {type(e).__name__}: {e}")
