"""Gab44 Telegram bot entrypoint.

Run locally:
    cd bot
    cp .env.example .env   # fill in TELEGRAM_BOT_TOKEN
    pip install -r requirements.txt
    python -m bot

Run in production (webhook behind Traefik):
    BOT_MODE=webhook python -m bot
"""
from __future__ import annotations

import asyncio
import logging
import sys

from telegram.ext import Application, ApplicationBuilder

from .api_client import BackendClient
from .config import load
from .handlers import register


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        stream=sys.stdout,
    )
    # python-telegram-bot is a bit chatty at INFO
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext").setLevel(logging.INFO)


async def _on_startup(app: Application) -> None:
    settings = app.bot_data["settings"]
    app.bot_data["api"] = BackendClient(settings.backend_url, settings.service_token)
    logging.info("Bot started in %s mode against %s", settings.mode, settings.backend_url)


async def _on_shutdown(app: Application) -> None:
    api: BackendClient = app.bot_data.get("api")
    if api:
        await api.aclose()


def main() -> None:
    _setup_logging()
    settings = load()

    builder = (
        ApplicationBuilder()
        .token(settings.bot_token)
        .post_init(_on_startup)
        .post_shutdown(_on_shutdown)
    )
    app = builder.build()
    app.bot_data["settings"] = settings

    register(app)

    if settings.mode == "polling":
        app.run_polling(drop_pending_updates=True)
    else:
        # In webhook mode python-telegram-bot starts an aiohttp server.
        # Traefik terminates TLS and forwards the path through.
        app.run_webhook(
            listen="0.0.0.0",
            port=settings.webhook_port,
            url_path=settings.webhook_path().lstrip("/"),
            webhook_url=settings.webhook_url(),
            secret_token=settings.webhook_secret,
            drop_pending_updates=True,
        )


if __name__ == "__main__":
    main()
