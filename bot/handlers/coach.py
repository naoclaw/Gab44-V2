"""Default text handler — routes plain messages to the AI coach (or friend)."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from ..api_client import BackendError
from ..formatters import chunk
from ._auth import require_jwt

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    jwt = await require_jwt(update, context)
    if not jwt:
        return

    api = context.application.bot_data["api"]
    mode = context.user_data.get("mode", "coach")
    session_id = context.user_data.get(
        "session_id", f"tg-coach-{update.effective_user.id}"
    )
    text = update.message.text

    await update.effective_chat.send_chat_action(ChatAction.TYPING)

    try:
        if mode == "friend":
            response = await api.friend_message(jwt, session_id, text)
        else:
            response = await api.coach_message(jwt, session_id, text)
    except BackendError as e:
        logger.warning("%s_message failed: %s", mode, e)
        if e.status == 429:
            await update.effective_chat.send_message(
                "You've hit your daily message limit on the free tier. "
                "Use /upgrade to keep chatting today."
            )
        else:
            await update.effective_chat.send_message(
                "Cosmic interference — couldn't get a response. Try again in a moment."
            )
        return

    reply = response.get("response") or response.get("message") or ""
    if not reply:
        await update.effective_chat.send_message("…")
        return

    for piece in chunk(reply):
        await update.effective_chat.send_message(piece)
