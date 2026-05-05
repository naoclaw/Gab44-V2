"""/chart — natal chart summary."""
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..api_client import BackendError
from ..formatters import format_chart
from ._auth import require_jwt

logger = logging.getLogger(__name__)


async def handle_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jwt = await require_jwt(update, context)
    if not jwt:
        return

    api = context.application.bot_data["api"]
    try:
        chart = await api.get_chart(jwt)
    except BackendError as e:
        logger.warning("get_chart failed: %s", e)
        if e.status == 404:
            await update.effective_chat.send_message(
                "I don't have your birth data yet. Add it on gab44.com and try again."
            )
        else:
            await update.effective_chat.send_message(
                "Couldn't fetch your chart right now. Please try again shortly."
            )
        return

    await update.effective_chat.send_message(
        format_chart(chart),
        parse_mode=ParseMode.MARKDOWN,
    )
