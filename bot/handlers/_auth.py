"""Shared helper: ensure the user has a JWT cached, prompt /start otherwise."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def require_jwt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    jwt = context.user_data.get("jwt")
    if jwt:
        return jwt
    await update.effective_chat.send_message(
        "Please /start first so I can link your Gab44 account."
    )
    return None
