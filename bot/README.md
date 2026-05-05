# Gab44 Telegram Bot

Conversational front door to the same FastAPI backend the website uses. Built on `python-telegram-bot v21`. See `../TELEGRAM_BOT.md` for the architecture and product reasoning behind every choice in here.

This is the **v1 skeleton** — `/start`, `/help`, `/chart`, `/today`, `/transits`, `/friend`, and a default text→coach handler. Onboarding wizard, payments, and daily push come in v1.1 and v1.2 (see roadmap in `../TELEGRAM_BOT.md`).

---

## Layout

```
bot/
├── __main__.py          # Entrypoint — builds Application, runs polling/webhook
├── config.py            # Reads env vars
├── api_client.py        # httpx wrapper around the FastAPI backend
├── formatters.py        # Markdown formatters for chart/today/transits
├── handlers/
│   ├── start.py         # /start — links Telegram user to a Gab44 account
│   ├── help.py          # /help
│   ├── chart.py         # /chart
│   ├── today.py         # /today (daily guidance)
│   ├── transits.py      # /transits
│   ├── friend.py        # /friend (toggle Saoul mode)
│   ├── coach.py         # default text → /api/chat or /api/friend/chat
│   └── _auth.py         # require_jwt helper
├── jobs/                # APScheduler jobs (daily push lands in v1.1)
├── tests/               # pytest suite (placeholder)
├── Dockerfile           # python:3.11-slim, runs `python -m bot`
├── requirements.txt
└── .env.example
```

---

## Run locally (polling)

```bash
cd bot
cp .env.example .env
# Edit .env: paste your TELEGRAM_BOT_TOKEN from @BotFather
pip install -r requirements.txt
python -m bot
```

Make sure the FastAPI backend is also running (`cd ../backend && uvicorn server:app --reload --port 8001`) and `BACKEND_URL=http://localhost:8001` in your bot `.env`.

Open Telegram, find your bot, send `/start`. The bot will call `POST /api/auth/telegram-link` on the backend.

---

## Backend prerequisite

The bot calls a new endpoint that doesn't exist on `main` yet:

- `POST /api/auth/telegram-link` — links a Telegram user ID to a Gab44 user (creates a lightweight account if no email match). Authenticated via the bot's `X-Service-Token` header.

This is **not yet implemented in `backend/server.py`** — it ships in the next backend PR. The skeleton here is ready to call it. If you run the bot before the backend endpoint exists, `/start` will reply with "couldn't reach the backend just now" and stop — no crash.

---

## Webhook mode (production on Hetzner + Traefik)

```bash
BOT_MODE=webhook \
TELEGRAM_BOT_TOKEN=... \
TELEGRAM_WEBHOOK_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))') \
BOT_WEBHOOK_BASE=https://bot.gab44.com \
BACKEND_URL=http://api:8001 \
SERVICE_TOKEN=... \
python -m bot
```

In docker-compose, route `bot.gab44.com` through Traefik to `bot:8080`. The bot calls `setWebhook` with the secret token on startup; Telegram includes that secret in every update via the `X-Telegram-Bot-Api-Secret-Token` header (PTB validates this automatically).

A starter compose snippet:

```yaml
services:
  bot:
    build: ./bot
    env_file: ./bot/.env
    networks: [traefik, gab44-internal]
    labels:
      traefik.enable: "true"
      traefik.http.routers.bot.rule: Host(`bot.gab44.com`)
      traefik.http.routers.bot.entrypoints: websecure
      traefik.http.routers.bot.tls.certresolver: letsencrypt
      traefik.http.services.bot.loadbalancer.server.port: "8080"
```

---

## Environment variables

| Var | Required | Purpose |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | From @BotFather |
| `BOT_MODE` | | `polling` (default) or `webhook` |
| `TELEGRAM_WEBHOOK_SECRET` | when webhook | Random 32-char string |
| `BOT_WEBHOOK_BASE` | when webhook | e.g. `https://bot.gab44.com` |
| `BOT_WEBHOOK_PORT` | | default `8080` |
| `BACKEND_URL` | ✅ | FastAPI base URL |
| `SERVICE_TOKEN` | ✅ | Shared secret with backend for `/api/auth/telegram-link` |
| `SENTRY_DSN` | | optional |

---

## What v1 deliberately does NOT do

- **No payments yet.** `/upgrade` is wired in v1.1 (Telegram Stars + Helio).
- **No daily push.** Scheduled job lands in v1.1 — depends on per-user timezone in the user document.
- **No onboarding wizard.** First-time users without birth data are pointed to the website. The `ConversationHandler`-based wizard is in the v1.1 PR.
- **No persistence between bot restarts** — `user_data` is in-memory. Fine for v1; we'll add `PicklePersistence` to a small SQLite file before production.

These are all tracked in `../TELEGRAM_BOT.md §10 Roadmap`.
