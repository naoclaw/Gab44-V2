"""/today — daily AI guidance."""
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..api_client import BackendError
from ..formatters import format_daily_guidance
from ._auth import require_jwt

logger = logging.getLogger(__name__)


async def handle_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jwt = await require_jwt(update, context)
    if not jwt:
        return

    api = context.application.bot_data["api"]
    try:
        guidance = await api.get_daily_guidance(jwt)
    except BackendError as e:
        logger.warning("get_daily_guidance failed: %s", e)
        await update.effective_chat.send_message(
            "Couldn't reach today's guidance — try again in a minute."
        )
        return

    await update.effective_chat.send_message(
        format_daily_guidance(guidance),
        parse_mode=ParseMode.MARKDOWN,
    )
