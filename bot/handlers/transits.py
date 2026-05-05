"""/transits — upcoming transits."""
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..api_client import BackendError
from ..formatters import format_transits
from ._auth import require_jwt

logger = logging.getLogger(__name__)


async def handle_transits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jwt = await require_jwt(update, context)
    if not jwt:
        return

    api = context.application.bot_data["api"]
    try:
        data = await api.get_transits(jwt)
    except BackendError as e:
        logger.warning("get_transits failed: %s", e)
        await update.effective_chat.send_message(
            "Couldn't load transits right now. Please try again shortly."
        )
        return

    await update.effective_chat.send_message(
        format_transits(data),
        parse_mode=ParseMode.MARKDOWN,
    )
