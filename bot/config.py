"""Environment-driven configuration for the Gab44 Telegram bot."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    webhook_secret: str
    mode: str  # "polling" | "webhook"
    webhook_base: str
    webhook_port: int
    backend_url: str
    service_token: str
    sentry_dsn: str

    def webhook_path(self) -> str:
        return f"/webhook/{self.webhook_secret}"

    def webhook_url(self) -> str:
        return f"{self.webhook_base.rstrip('/')}{self.webhook_path()}"


def load() -> Settings:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set. Copy .env.example → .env and fill it in."
        )

    mode = os.environ.get("BOT_MODE", "polling").lower()
    if mode not in ("polling", "webhook"):
        raise RuntimeError(f"BOT_MODE must be 'polling' or 'webhook' (got {mode!r}).")

    webhook_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    if mode == "webhook" and not webhook_secret:
        raise RuntimeError("TELEGRAM_WEBHOOK_SECRET is required when BOT_MODE=webhook.")

    return Settings(
        bot_token=bot_token,
        webhook_secret=webhook_secret,
        mode=mode,
        webhook_base=os.environ.get("BOT_WEBHOOK_BASE", "").rstrip("/"),
        webhook_port=int(os.environ.get("BOT_WEBHOOK_PORT", "8080")),
        backend_url=os.environ.get("BACKEND_URL", "http://localhost:8001").rstrip("/"),
        service_token=os.environ.get("SERVICE_TOKEN", ""),
        sentry_dsn=os.environ.get("SENTRY_DSN", ""),
    )
