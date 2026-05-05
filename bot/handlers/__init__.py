"""Handler registration helpers."""
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from . import chart, coach, friend, help as help_handler, start, today, transits


def register(app: Application) -> None:
    """Wire all bot handlers onto the python-telegram-bot Application."""
    app.add_handler(CommandHandler("start", start.handle_start))
    app.add_handler(CommandHandler("help", help_handler.handle_help))
    app.add_handler(CommandHandler("chart", chart.handle_chart))
    app.add_handler(CommandHandler("today", today.handle_today))
    app.add_handler(CommandHandler("transits", transits.handle_transits))
    app.add_handler(CommandHandler("friend", friend.handle_friend_toggle))
    # Anything that isn't a command is forwarded to the AI coach (or friend
    # if the user is in friend mode — set inside coach.handle_message).
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, coach.handle_message))
