# Gab44 — Phase 3 Telegram Bot Architecture

> **The bot is a conversational front door to the same backend.** It does not own the user, the chart, or the AI prompts — it borrows them from `backend/server.py` via a thin internal API. Built on `python-telegram-bot v21` (async). Deployed alongside FastAPI on the Hetzner VPS, behind Traefik. Pays via **Telegram Stars** for digital goods (App Store / Play compliant) and **Helio** for crypto power-users.

---

## 1. What the Bot Does

Five conversational surfaces, each backed by an existing FastAPI route:

| Bot command / button | Backend it calls | Mode |
|---|---|---|
| `/start` | `POST /api/auth/telegram-link` (NEW) | Onboarding — link Telegram ID to a Gab44 account or create a new one. |
| `/chart` | `GET /api/chart/me` | Sends a formatted natal chart summary (text + optional image). |
| `/today` | `GET /api/guidance/daily` | Daily horoscope/guidance card. Also fired by a daily scheduled job at user's local 8am. |
| `/transits` | `GET /api/transits/upcoming` | Upcoming transit highlights. |
| `/coach` (default conversation mode) | `POST /api/chat` | AI coach — every text message routes here when no other intent matches. |
| `/friend` | `POST /api/friend/chat` | Switch to Saoul (warmer persona). |
| `/compatibility` | `POST /api/compatibility/analyze` | Inline conversation: collects partner's birth data, returns the report. |
| `/numerology` | `GET /api/numerology/profile` | Numerology card. |
| `/upgrade` | `POST /api/payments/telegram-stars-invoice` (NEW) or Helio link | Subscription via Stars or Helio. |
| `/settings` | Inline buttons | Toggle daily push, change birth data, switch Coach/Friend. |
| `/help` | (static) | Command list. |

**Persona principle:** the bot is the *AI coach speaking through Telegram*. It uses the same prompts, the same chart context, the same daily-cap logic. If the user pays for `enthusiast` on the web, they get enthusiast limits in the bot — same `users` row, same `subscription_tier`.

---

## 2. Architecture

```
┌────────────────────┐        Long polling (dev) /         ┌────────────────────┐
│ Telegram Bot API   │  ◀───  Webhook (prod)         ───▶ │  bot/ (asyncio)    │
└────────────────────┘                                    │  python-telegram-  │
                                                          │  bot v21           │
                                                          └────────┬───────────┘
                                                                   │ HTTP (internal)
                                                                   │ Bearer "service token"
                                                                   ▼
                                                          ┌────────────────────┐
                                                          │ FastAPI server.py  │
                                                          │ (existing)         │
                                                          └────────┬───────────┘
                                                                   ▼
                                                          ┌────────────────────┐
                                                          │ MongoDB Atlas      │
                                                          │  + new collection: │
                                                          │  telegram_links    │
                                                          └────────────────────┘
```

### Process model

- One Python process: `python -m bot` (entrypoint at `bot/__main__.py`).
- Deployed as a **separate Traefik service** (or systemd unit) on the same Hetzner box.
- Webhook endpoint exposed at `https://bot.gab44.com/webhook/<TELEGRAM_WEBHOOK_SECRET>`. Traefik routes by host. The webhook secret is rotated quarterly.
- Health check: `GET /healthz` returns 200 if the bot is connected to Telegram and can reach the backend.

### Why a separate service, not a route inside `server.py`?

- **Failure isolation.** A spammy bot user shouldn't slow down the web app. Restart bot ≠ restart API.
- **Long-poll vs webhook flexibility.** Easy to flip the bot to polling for local dev without touching the API.
- **Permissions.** The bot authenticates to the API with a single service token + a Telegram-user header, so we can audit/revoke independently.
- **Code reuse.** It still imports the *pure* modules (`backend.astro_calculator`, `backend.numerology`, `backend.gematria`) directly for offline computation paths if needed, but networked features go through the API.

### Why Telegram is **not** stuffed into `server.py`

The webhook handler must respond inside ~5 seconds or Telegram retries. AI calls take longer. The bot acks immediately, then sends the answer asynchronously. That state-machine is fundamentally different from the request-response shape of FastAPI routes.

---

## 3. New Backend Endpoints (added in Phase 4)

These live in `backend/server.py` (initially) so the bot can call them with a service token.

### `POST /api/auth/telegram-link`

Body: `{ telegram_user_id: int, telegram_username: str?, first_name: str?, language_code: str?, link_token: str? }`

- If `link_token` is provided (user clicked "Link your Telegram" in the web app), associate this Telegram ID with the existing Gab44 user.
- Otherwise create a **lightweight account** keyed by Telegram ID. They can later add an email + password to upgrade to a full account.
- Returns `{ user_id, subscription_tier, has_birth_data: bool, jwt: <short-lived for impersonation> }`.

A new collection `telegram_links` keys `{ telegram_user_id → user_id, linked_at, locale }`.

### `POST /api/payments/telegram-stars-invoice`

Returns a Telegram `createInvoiceLink` URL the bot embeds in the chat. Uses the **Stars** currency (no real-money rails, App-Store-safe). Server records the pending invoice; webhook from Telegram (`successful_payment`) goes to a new `POST /api/payments/telegram-webhook` that flips `subscription_tier`.

### `POST /api/payments/helio-checkout`

Calls Helio's API to create a checkout link for crypto payment (USDC on Solana / Polygon). Helio's webhook (`POST /api/payments/helio-webhook`) confirms and upgrades tier. Helio is opt-in (`/upgrade crypto` subcommand) — Stars is the default.

### `GET /api/internal/user/{user_id}`

Auth: service token only (header `X-Service-Token`). Returns the full user document the bot needs to render menus and enforce tier limits. **Internal-only**, never exposed via Traefik to the public.

### `GET /api/transits/upcoming` and others

No change — the bot calls them with the user's JWT (returned from `telegram-link`).

---

## 4. The `bot/` Module

```
bot/
├── __main__.py           # Entrypoint: builds Application, registers handlers, runs polling/webhook
├── config.py             # Reads env: TELEGRAM_BOT_TOKEN, BACKEND_URL, SERVICE_TOKEN, WEBHOOK_SECRET
├── api_client.py         # httpx.AsyncClient wrapper for backend; manages per-user JWT cache
├── handlers/
│   ├── start.py          # /start + onboarding state machine (collect birth data)
│   ├── chart.py          # /chart, /numerology
│   ├── today.py          # /today
│   ├── transits.py       # /transits
│   ├── coach.py          # default text → coach; /friend toggle
│   ├── compatibility.py  # ConversationHandler: name → date → time → place → result
│   ├── upgrade.py        # /upgrade → Stars invoice or Helio link
│   ├── settings.py       # /settings (inline keyboard)
│   └── help.py           # /help, fallback for unknown commands
├── jobs/
│   └── daily_push.py     # APScheduler: per-user 8am-local daily-guidance push
├── formatters.py         # Markdown formatters for chart/transits/numerology
└── tests/
    └── test_handlers.py
```

### Onboarding state machine (`/start`)

```
/start
  ├─► If telegram_user_id is already linked → "Welcome back, ✨" + main menu
  └─► If not linked
        ├─► "Link existing Gab44 account" → ask for email; bot sends a one-time link token via web → user clicks → linked.
        └─► "Create new account here"
              → ask for first name
              → ask for date of birth (date keyboard via inline buttons)
              → ask for time of birth (or "I don't know" → defaults to noon, flagged)
              → ask for birthplace (free text → backend Mapbox/cities lookup)
              → backend creates lightweight user, returns JWT → bot caches → main menu.
```

The state machine is a `ConversationHandler` from `python-telegram-bot`. State is stored in `Application.user_data` (in-memory, survives reconnects via `PicklePersistence` to a small SQLite file).

### Default text → coach

If a user just types text without a command, the bot routes to `POST /api/chat`:

1. Bot acks (`"✨ ..."` typing indicator).
2. Calls `/chat` (with the user's session_id from `user_data`).
3. Streams the answer in chunks of ≤4096 chars (Telegram message limit).

This makes the bot feel like a Telegram-native AI friend instead of a button-heavy menu app.

---

## 5. Payment Strategy

### A. Telegram Stars (default, recommended)

- Native to Telegram. No 30% Apple/Google cut. Compliant with platform policies for digital goods.
- Backend creates an invoice via `Bot.create_invoice_link(prices=[LabeledPrice("Enthusiast", stars_amount)])`.
- User pays in-chat. Telegram sends `successful_payment` update → bot forwards to `POST /api/payments/telegram-webhook` → backend flips `subscription_tier` to `enthusiast`/`advanced`/`professional`.
- Stars-to-USD rate is roughly 100 stars = $1 (Telegram tunes it). We set tier prices in stars (e.g., 1000 stars ≈ $10/mo for enthusiast) and adjust quarterly.

### B. Helio (crypto, opt-in)

- USDC on Solana or Polygon. Useful for Web3-curious users and high-ticket lifetime plans.
- `/upgrade crypto` → bot returns a Helio checkout link (also viewable as a QR code).
- Helio webhook → `POST /api/payments/helio-webhook` (HMAC-verified) → tier upgrade.

### C. Web (Stripe)

Already exists. We don't deep-link to Stripe inside Telegram (Apple frowns on it). For users who want to pay by card, the bot tells them: *"Open gab44.com/pricing on the web — your account is the same."*

### Tier model alignment

- The `subscription_tier` field on the user document is the single source of truth.
- All three rails (Stripe, Stars, Helio) write the same field.
- Daily-cap enforcement in `server.py` already keys off `subscription_tier` — works unchanged.

---

## 6. Daily Push (the killer feature)

A scheduled job sends each opted-in user their daily guidance at 8am in their local timezone.

- `jobs/daily_push.py` runs every 15 minutes.
- Queries `telegram_links` for users where `now_in_user_tz` is within 15 min of `daily_push_time` (default 8am) and `daily_push_enabled = true`.
- For each: calls `GET /api/guidance/daily` (which is cached server-side, so 100k users at the same hour are 100k DB reads, not 100k LLM calls).
- Formats and sends to the chat.
- Recovers gracefully if Telegram returns 429 (back off + reschedule).

The user's timezone is inferred from birthplace (we already have `timezonefinder` in `requirements.txt`) or set explicitly in `/settings`.

---

## 7. Security

| Concern | Mitigation |
|---|---|
| Bot token leak | Read from env. Never logged. Rotate via BotFather → re-deploy. |
| Webhook spoofing | URL contains `TELEGRAM_WEBHOOK_SECRET` (random 32-char). Only Telegram + ops know it. Verify `X-Telegram-Bot-Api-Secret-Token` header on receive. |
| Service-token compromise | Single rotating secret. Backend rejects requests to `/api/internal/*` from anywhere except `127.0.0.1` AND with valid token. |
| Rate-limit abuse | All bot → backend calls go through the same slowapi limiter, scoped per `user_id` so a noisy bot user doesn't penalize a noisy web user. |
| Prompt injection via Telegram message | Same sanitization as the web `chat` endpoint (`server.py:1950-1953` style). |
| Account-takeover via Telegram → web | When linking, send a 6-digit code to the user's email; they paste it back to the bot to confirm ownership. |
| GDPR / data export | `/forgetme` command triggers the same user-deletion path the web will (TODO: not yet implemented in `server.py` — flagged in REVIEW). |

---

## 8. Deployment (Hetzner + Traefik)

```
                        Internet
                            │
                            ▼
                       ┌──────────┐
                       │ Traefik  │  ── 443
                       └────┬─────┘
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
         api.gab44.com   bot.gab44.com   gab44.com
         (FastAPI)       (PTB webhook)   (React build)
              │
              ▼
         MongoDB Atlas
```

- `bot.gab44.com` → Traefik → bot container on port 8080.
- TLS terminated at Traefik (Let's Encrypt).
- Both API and bot share `CORS_ORIGINS`, `MONGO_URL`, `OPENAI_API_KEY` via the same secret store.
- Bot has its own env: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `BACKEND_INTERNAL_URL=http://api:8001`, `SERVICE_TOKEN=<32-byte hex>`.

A docker-compose snippet is included in Phase 4 scaffolding.

---

## 9. Observability

- Bot logs every command + latency to stdout (Traefik captures).
- Sentry SDK (optional, gated by `SENTRY_DSN` env) catches handler exceptions with the username + command pre-attached.
- A `/admin botstats` command (visible to ADMIN_EMAILS users only — checked by linking telegram_user_id to user.role) prints DAU, command counts, error rate.

---

## 10. Roadmap

### v1 (Phase 4 — this iteration)
- Repo skeleton + `__main__.py` that registers `/start`, `/help`, `/chart`, `/today`, `/coach` (default text), `/friend`.
- `telegram_links` collection + `POST /api/auth/telegram-link` endpoint.
- Long-polling mode for local dev.
- README.md in `bot/` with run instructions.

### v1.1
- Stars invoice flow (`/upgrade`).
- Daily push job.
- Compatibility conversation flow.

### v2
- Inline mode (`@gab44bot today` from any chat).
- Voice messages → Whisper → coach.
- Image generation: render the natal chart wheel and send as a photo.
- Helio crypto payments.
- Webhook mode for production.

---

## 11. Open Questions for Product

1. Do we want the bot to be **public** (anyone can `/start`) or **invite-only** (existing Gab44 users only)? Default plan: public, with a separate `bot_users` row for telegram-only signups.
2. Do telegram-only users get a free tier (`seeker` defaults) or do they need to verify email first to access AI? Default plan: `seeker` works without email; AI quota requires verification.
3. Stars pricing: how many stars = $1 to us today? Set quarterly? Default plan: track Telegram's published rate, recompute monthly via a cron.
4. Group chats: do we allow the bot in groups? Default plan: **no** in v1. Personal data + per-user context = 1:1 only.

These need product/founder sign-off before v1.1.
