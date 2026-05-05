"""/help command."""
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


HELP = (
    "*Gab44 commands*\n\n"
    "/start — link your account and onboard\n"
    "/today — your daily guidance\n"
    "/chart — your natal chart summary\n"
    "/transits — upcoming transits\n"
    "/friend — switch to Saoul (warmer companion mode)\n"
    "/help — this menu\n\n"
    "_Just type a message and I'll respond as your AI coach._"
)


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(HELP, parse_mode=ParseMode.MARKDOWN)
