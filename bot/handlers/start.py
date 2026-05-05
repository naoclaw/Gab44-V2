"""/start handler — onboarding and Telegram-account linking."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..api_client import BackendError

logger = logging.getLogger(__name__)


WELCOME_NEW = (
    "Welcome to *Gab44* ✨\n\n"
    "I'm your cosmic coach in Telegram. I read your natal chart, deliver daily "
    "guidance, and chat with you whenever you have a question for the universe.\n\n"
    "To get started I need three things:\n"
    "  1. Your name\n"
    "  2. Your date of birth\n"
    "  3. Your birthplace (city, country)\n\n"
    "_Onboarding flow lands in v1.1 — for now please complete your profile on_ "
    "[gab44.com](https://gab44.com) _and come back here._"
)

WELCOME_BACK = (
    "Welcome back, {name} 🌙\n\n"
    "Try */today* for your daily guidance, */chart* for your natal chart, or "
    "just send me a message and I'll respond as your AI coach."
)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    api = context.application.bot_data["api"]
    try:
        link = await api.link_telegram(
            telegram_user_id=user.id,
            telegram_username=user.username,
            first_name=user.first_name,
            language_code=user.language_code,
        )
    except BackendError as e:
        logger.warning("link_telegram failed for %s: %s", user.id, e)
        await update.effective_chat.send_message(
            "Sorry, I couldn't reach the Gab44 backend just now. "
            "Please try again in a moment."
        )
        return

    # Cache the JWT and a coach session id for later messages.
    context.user_data["jwt"] = link.get("jwt")
    context.user_data["user_id"] = link.get("user_id")
    context.user_data["session_id"] = f"tg-coach-{user.id}"
    context.user_data["mode"] = "coach"

    if link.get("has_birth_data"):
        await update.effective_chat.send_message(
            WELCOME_BACK.format(name=user.first_name or "Seeker"),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await update.effective_chat.send_message(
            WELCOME_NEW,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
