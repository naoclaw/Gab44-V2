"""/friend — toggle between Coach and Saoul (Friend) personas."""
from telegram import Update
from telegram.ext import ContextTypes


async def handle_friend_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current = context.user_data.get("mode", "coach")
    if current == "friend":
        context.user_data["mode"] = "coach"
        context.user_data["session_id"] = f"tg-coach-{update.effective_user.id}"
        await update.effective_chat.send_message(
            "Back to coach mode. I'll focus on practical, grounded guidance."
        )
    else:
        context.user_data["mode"] = "friend"
        context.user_data["session_id"] = f"tg-friend-{update.effective_user.id}"
        await update.effective_chat.send_message(
            "Hi, I'm Saoul 🌹 — your warmer, friendlier companion. "
            "Tell me what's on your mind."
        )
