# Gab44 — Phase 1 Review

> **Scope.** Top-to-bottom audit of the current codebase as of branch `main` (commit `cfefa89`). Goal: establish the ground truth before we (a) ship a mobile app and (b) launch a Telegram bot.

---

## 1. Architecture at a Glance

```
                    ┌──────────────────────────────────┐
                    │   React 19 SPA (frontend/)       │
                    │   CRA + Craco + Tailwind +       │
                    │   shadcn/Radix + react-router 7  │
                    └─────────────┬────────────────────┘
                                  │ axios (Bearer JWT)
                                  ▼
                    ┌──────────────────────────────────┐
                    │   FastAPI app (backend/server.py)│
                    │   ~2,900 lines, all routes here  │
                    │   gunicorn + uvicorn workers     │
                    └─────────────┬────────────────────┘
                                  │ Motor async driver
                                  ▼
                    ┌──────────────────────────────────┐
                    │   MongoDB Atlas                  │
                    │   gab44.6ca0nct.mongodb.net      │
                    │   DB: gab44                      │
                    └──────────────────────────────────┘

External: OpenAI GPT-4o · Stripe · SendGrid · OneSignal · Mapbox · Swiss Ephemeris (in-process)
```

### Frontend (`frontend/`)
- **React 19** with `react-router-dom@7.5.1`, Tailwind 3, shadcn/ui (Radix primitives), Sonner for toasts, axios for HTTP, recharts for visualization, `next-themes` for dark/light.
- Build tool is **CRA + Craco** (`craco.config.js`). Webpack — not Vite. Path alias `@/*` configured in `jsconfig.json`.
- Single `App.js` defines `AuthContext`, `ProtectedRoute`, `AdminRoute`, and 17 routes inside `BrowserRouter`. Auth token stored as `localStorage["gab44_token"]`. A global axios interceptor (`App.js:55-82`) auto-logs-out on 401 and toasts the user.
- Pages: `LandingPage`, `AuthPage`, `Dashboard`, `ChatPage`, `FriendPage`, `ChartPage`, `TransitsPage`, `CompatibilityPage`, `NumerologyPage`, `GematriaPage`, `PricingPage`, `SettingsPage`, `ShareChartPage`, `PublicChartPage`, `VerifyEmailPage`, `ResetPasswordPage`, `AdminPage`.
- 45 shadcn components in `components/ui/` (full Radix coverage). One custom `ErrorBoundary`.
- Two contexts: `ThemeContext` (dark/light) and `ReadingModeContext`.

### Backend (`backend/`)
- **FastAPI 0.110** + Motor 3.3 (async MongoDB) + slowapi rate limiting + bcrypt + PyJWT.
- Single 127KB `server.py` (~2,900 lines) holds **every** route. Functional — but a serious refactor target before Telegram and mobile traffic land.
- Submodules:
  - `astro_calculator.py` — **active** Swiss-Ephemeris engine. Used by all chart/transit endpoints.
  - `astro_engine.py` — **dead code.** Never imported. Listed in README but unused.
  - `numerology.py` — Pythagorean engine (Life Path, Expression, Soul Urge, Personality, Personal Year, plus 11/22/33 master numbers).
  - `gematria.py` — Chaldean + English Ordinal calculator.
  - `cities.py` — 327-city offline geocoding fallback for when Mapbox is absent.
  - `payments.py` — Stripe wrapper (Price-ID-based) — **inconsistent with `server.py`** (see §6).
- Container: `python:3.11-slim` + `build-essential` (needed to compile `pyswisseph`). `gunicorn -w 2 -k uvicorn.workers.UvicornWorker --timeout 120`.

### Database
- MongoDB Atlas (free / shared tier). Collections used:
  - `users` (unique on `email` & `id`; sparse on `stripe_customer_id`, `password_reset_token`)
  - `chat_messages` and `friend_messages` (separate streams for Coach vs. Saoul)
  - `birth_charts` (unique `user_id`; sparse `share_token`)
  - `compatibility_reports` (`id`, `user_id`)
  - `daily_guidance` (compound unique `[user_id+date]`)
  - `newsletter_subscribers` (unique `email`)
  - `contact_messages` (indexed `created_at`)
  - `transit_cache` (per the test `test_transit_cache.py`)
- All indexes are created in the FastAPI `startup` event.

### Deployment surface today
- Three deployment configs are present in the repo, none currently in use cleanly:
  - **AWS / ECS Fargate + S3 + CloudFront** — fully described in README, GitHub Actions workflow at `.github/workflows/deploy-aws.yml`.
  - **Vercel** — `vercel.json` + `api/index.py` shim that imports `backend.server`. *Note:* `api/index.py` exposes `handler = app`, but `pyswisseph` requires a compiled C extension and won't survive Vercel's Python runtime cleanly without a custom layer. **Likely broken on Vercel today.**
  - **Railway / Nixpacks** — `backend/railway.toml` + `nixpacks.toml`. Likely healthy.
- Recent commits (`cfefa89`, `c64049a`) show the team was iterating on Vercel routing. Phase 4 plan moves backend to **Hetzner VPS at 135.181.44.161 via Traefik**, which is the right call for an app that needs `pyswisseph` and persistent connections.

---

## 2. What Works ✅

| Area | Status |
|---|---|
| Auth (register/login/JWT/me, email verify, reset password) | Working. Timing-resistant login (`server.py:1075` uses `_DUMMY_HASH`), bcrypt, rate-limited. |
| Birth chart calc (`pyswisseph`, Placidus houses, 5 major aspects, retrograde, Lilith, North Node, Chiron) | Working. Cached in `birth_charts` with `BIRTH_CHART_SCHEMA_VERSION` for safe invalidation. |
| Transits (outer planets vs natal) | Working. ~250 lines of hardcoded interpretations (`server.py:1655-1900`) — brittle, but functional. |
| Numerology profile + Gematria calculator | Working. Full Pythagorean profile + Chaldean/English Ordinal. |
| AI Coach + AI Friend (Saoul) | Working. Each has its own session collection, persona, tier-based daily message limit. |
| Daily Guidance | Working. GPT-4o JSON mode, 24-hour cache per user, **graceful static fallback** when LLM is absent or errors. |
| Compatibility (synastry + composite + AI narrative) | Working. 5 relationship types, weighted scoring. |
| Stripe Checkout + Customer Portal + webhook | Working in production-with-secret mode. **See §6 for the bypass risk.** |
| SendGrid email (4 typed senders) | Working. Non-blocking on send failure. |
| OneSignal push registration + admin daily blast | Working. |
| Public chart sharing (revocable token) | Working. |
| Admin RBAC (`role: "admin"`, `ADMIN_EMAILS` bootstrap) | Working. |
| Tests | 7 test files in `backend/tests/` covering Swiss Ephemeris, compatibility, RBAC, CORS, error handling, transit cache, API integration. |

---

## 3. What Is Broken or Risky 🚨

### Critical
| # | Severity | Where | Issue |
|---|---|---|---|
| 1 | **CRITICAL** | `server.py:2434` (webhook handler) | If `STRIPE_WEBHOOK_SECRET` is unset, the webhook **accepts unsigned events**. An attacker can forge `checkout.session.completed` to upgrade arbitrary user IDs to `professional`. Must hard-fail on missing secret in production. |
| 2 | HIGH | Email verify (`server.py:1089-1107`), Password reset (`1154-1177`) | The token-expiry constants exist (`EMAIL_VERIFY_EXPIRY_HOURS=48`, `PASSWORD_RESET_EXPIRY_HOURS=1`) but **the corresponding timestamps are never written to or checked from the user document**. A leaked token is valid forever. |
| 3 | HIGH | `payments.py` vs `server.py:108-112` | Two payment code paths coexist with **different pricing models**: `payments.py` uses Stripe **Price IDs** (`STRIPE_PRICE_ENTHUSIAST`, etc.); `server.py` uses **inline amounts** in `STRIPE_PLAN_PRICES`. Whichever is wired up wins; the other is dead code that will silently take over if imported. |
| 4 | HIGH | Pricing inconsistency | The `/api/pricing` payload says `enthusiast = $9.99`, `advanced = $29.99`. The Stripe inline-amount checkout charges **$19.99** and **$49.99**. Customers will see one price and be charged another. |
| 5 | HIGH | Vercel deploy path (`api/index.py`) | `pyswisseph` is a compiled C extension. The Vercel Python runtime won't include the binary unless a custom layer / build hook is added. The recent commit `cfefa89` ("Fix Vercel routes configuration") suggests the team knows this is shaky. **Hetzner VPS migration in Phase 4 fixes this.** |

### Medium
| # | Where | Issue |
|---|---|---|
| 6 | JWT / session | No server-side revocation. `logout()` only clears `localStorage`. A stolen token is valid for 7 days. No refresh-token mechanism. |
| 7 | `server.py:2627-2637` | `/api/admin/upgrade-all-users` mass-upgrades every user to `advanced` with no confirmation, no audit log. One stray click in Swagger and tier accounting is gone. |
| 8 | `server.py:1226-1230` | Daily-message-limit query counts only `role: "user"` messages but the time window is computed from "today UTC" with potential off-by-one at the boundary. |
| 9 | `server.py:1563-1577` | `/api/chart/public/{share_token}` has **no rate limit**. Public links can be scraped at line speed. |
| 10 | `server.py:2837-2846` | If `CORS_ORIGINS` is `*` and `FRONTEND_URL` looks like production, a warning is **logged** but the wildcard is still applied. Should refuse to start. |

### Low
| # | Where | Issue |
|---|---|---|
| 11 | `astro_engine.py` (whole file) | Dead code. Never imported. Delete or wire up. |
| 12 | Transit interpretations (`server.py:1655-1900`) | Hardcoded library; new (transiting → natal × aspect) tuples have no fallback narrative. Move to LLM-generated + cached. |
| 13 | OneSignal failures (`server.py:2323-2348`) | `send_onesignal_notification()` swallows errors and returns `False`. Failed pushes are invisible — no log, no retry. |
| 14 | Admin actions | No audit log for tier changes, role changes, mass upgrades. |
| 15 | `frontend/src/App.js:303-304` | The 404 `<Route path="*">` is **placed outside `<Routes>`**. It will never match — every unknown path returns a blank page instead of `NotFoundPage`. Easy fix. |

---

## 4. API Surface (current)

Grouped by feature. All routes are prefixed with `/api`. **🔒 = JWT required**, **👑 = admin only**, **🌐 = public**.

| Group | Method · Path | Auth | Notes |
|---|---|---|---|
| **Auth** | `POST /auth/register` | 🌐 | Rate-limited 10/hr. Sends verification email. |
| | `POST /auth/login` | 🌐 | Rate-limited 20/min. Timing-resistant. |
| | `GET /auth/verify-email?token=` | 🌐 | Token expiry not enforced. |
| | `POST /auth/resend-verification` | 🔒 | |
| | `POST /auth/forgot-password` | 🌐 | Rate-limited 5/hr. |
| | `POST /auth/reset-password` | 🌐 | Token expiry not enforced. |
| | `GET /auth/me` | 🔒 | |
| | `PUT /auth/me` | 🔒 | Updates birth_date / birth_place / coords. Triggers chart recalc downstream. |
| **Chart** | `GET /chart/me?recalculate=true` | 🔒 | Cached in `birth_charts` w/ schema versioning. |
| | `POST /chart/share` | 🔒 | Mints share token. |
| | `DELETE /chart/share` | 🔒 | Revokes. |
| | `GET /chart/public/{share_token}` | 🌐 | **No rate limit.** Wildcard CORS. |
| **Transits** | `GET /transits/upcoming` | 🔒 | ~30 hardcoded interpretation entries. |
| **Daily Guidance** | `GET /guidance/daily` | 🔒 | GPT-4o JSON; static fallback. 24h cache. |
| **Coach (Chat)** | `POST /chat` | 🔒 | Rate-limited 60/min. Per-tier daily caps. |
| | `GET /chat/history/{session_id}` | 🔒 | |
| | `GET /chat/sessions` | 🔒 | |
| | `DELETE /chat/session/{session_id}` | 🔒 | |
| **Friend (Saoul)** | `POST /friend/chat` | 🔒 | Same shape, separate persona. |
| | `GET /friend/history/{session_id}` | 🔒 | |
| | `GET /friend/sessions` | 🔒 | |
| | `DELETE /friend/session/{session_id}` | 🔒 | |
| **Numerology** | `GET /numerology/me` | 🔒 | |
| | `GET /numerology/profile` | 🔒 | Full Pythagorean profile. |
| **Gematria** | `POST /gematria/calculate` | 🌐 | No auth — likely intentional for landing-page demo. |
| **Compatibility** | `POST /compatibility/analyze` | 🔒 | |
| | `GET /compatibility/reports` | 🔒 | |
| | `GET /compatibility/reports/{report_id}` | 🔒 | |
| **Pricing** | `GET /pricing` | 🌐 | Hardcoded tier list. **Mismatched with Stripe amounts.** |
| **Payments** | `POST /payments/create-checkout-session` | 🔒 | |
| | `POST /payments/portal` | 🔒 | |
| | `POST /payments/webhook` | 🌐 | **Bypassable if secret unset.** |
| **Push** | `POST /notifications/register-device` | 🔒 | |
| | `POST /notifications/send-daily` | 👑 | Broadcast to all OneSignal subs. |
| **Newsletter / Contact** | `POST /subscribe` | 🌐 | |
| | `POST /contact` | 🌐 | |
| **Admin** | `POST /admin/upgrade-all-users` | 👑 | Dangerous; no audit log. |
| | `GET /admin/stats` | 👑 | |
| | `GET /admin/users` | 👑 | Paginated. |
| | `PUT /admin/users/{user_id}/tier` | 👑 | |
| | `PUT /admin/users/{user_id}/role` | 👑 | |
| **Health** | `GET /` | 🌐 | API info. |
| | `GET /health` | 🌐 | No DB check — just returns 200. Should ping Mongo. |

---

## 5. AI Integrations

- **OpenAI GPT-4o is the only LLM in the codebase.** Searched: there is **no xAI/Grok integration** anywhere. The mission brief mentions Grok — that's aspirational. Flag for product clarity before mobile launch.
- Client init: `openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None` (`server.py:95`). All four call sites hardcode `model="gpt-4o"`.
- Four prompt construction patterns:
  1. **AI Coach** (`server.py:849-945`) — system prompt injects user profile + planets + numerology + aspects; last 10 messages of session history; user message; → GPT-4o.
  2. **AI Friend** (`server.py:948-1013`) — same shape, warmer "Saoul" persona, no advice mode.
  3. **Daily Guidance** (`server.py:1909-2049`) — JSON-mode prompt with sanitized user fields (`server.py:1950-1953` blocks prompt-injection vectors). Static fallback (`2012-2039`) makes the feature robust.
  4. **Compatibility narrative** (`server.py:796-842`) — synastry + composite chart + numerology comparison fed into a narrative-generation prompt.
- **All AI features degrade gracefully** when `OPENAI_API_KEY` is absent. Good for staging.
- **No** prompt caching, response caching beyond daily-guidance, embedding store, or RAG. Coach/Friend re-pay full context every turn — fine today, expensive at Telegram-bot scale.

### Recommendations (forward-looking)
- Add a thin **`ai/` subpackage** that wraps the four call patterns. Mobile + Telegram should not duplicate prompt strings.
- Adopt **OpenAI prompt caching** on the system prompt (≥1024 tokens of chart context is identical across turns of one conversation) — easy 50-90% cost cut.
- Consider routing daily-guidance to **Claude Haiku 4.5** or **GPT-4o-mini** for cost; keep GPT-4o for coach.
- If "Grok" is desired, abstract the model selection behind a single `generate_text(messages, mode)` helper.

---

## 6. Astrology Engine

- **Active engine: `astro_calculator.py`** (34KB). `astro_engine.py` (19KB) is **dead code**.
- `pyswisseph 2.10.3.2` initialized with built-in Moshier ephemeris — no external `.se1` files needed (`astro_calculator.py:27 swe.set_ephe_path('')`).
- Computes:
  - 10 traditional planets + True Node + Chiron + Black Moon Lilith (mean apogee).
  - **Placidus** house system + Ascendant + Midheaven.
  - 5 major aspects with applying/separating distinction; orbs 6–8°.
  - Retrograde flag from `swe.calc_ut` speed.
  - Synastry aspects (`server.py:659-713`) and composite chart midpoints (`server.py:714-771`).
  - Current transits of outer planets (Jupiter → Pluto) against natal chart.
- Caching: `birth_charts` collection, schema-versioned (`BIRTH_CHART_SCHEMA_VERSION = 1`). Bump the constant to invalidate every cache row at once. Solid pattern.
- **Quality bar:** the math is correct against reference charts (covered in `tests/test_swiss_ephemeris.py`). This is the most reusable, valuable piece of the codebase — **it must follow us into the Telegram bot, unchanged.**

---

## 7. Auth System

- JWT (HS256, `server.py:90`) signed with `JWT_SECRET`. Expiration: 7 days. Payload: `{user_id, exp}`.
- bcrypt password hashing with default salt rounds. Constant-time compare via `bcrypt.checkpw()`.
- Email verification token: `secrets.token_urlsafe(32)`. **Expiry not enforced** (token_created_at not stored/checked).
- Password reset token: same shape. **Expiry not enforced** either.
- Admin RBAC: `role` field on user doc + `ADMIN_EMAILS` env auto-grants on login.
- **No refresh tokens, no logout-side-effects, no device list.** For a mobile app this is acceptable v1; for a Telegram bot we'll need a separate auth path (linking Telegram account → Gab44 user ID).

---

## 8. Design System (Cosmic Luxury)

The frontend already ships a tasteful, branded design system. Key tokens (`frontend/src/index.css`):

| Token | Light | Dark |
|---|---|---|
| `--background` | `35 40% 95%` (warm parchment) | `240 15% 6%` (cosmic night) |
| `--foreground` | `240 10% 15%` | `40 20% 96%` |
| `--primary` | `38 92% 50%` (gold) | `42 92% 55%` (gold) |
| `--accent` | `245 50% 95%` (lavender) | `240 10% 14%` |
| `--radius` | `0.75rem` | `0.75rem` |

- **Type scale:** Cinzel (serif, headings) + Manrope (sans, body) + JetBrains Mono (code). Already loaded via Google Fonts in `public/index.html`.
- **Signature components:** `.glass-card`, `.glow-button`, `.cosmic-gradient`, `.cosmic-page-bg`, `.zodiac-badge`, `.chat-bubble-friend` (rose-tinted Saoul bubbles), `.transit-card`.
- **Animations:** `fadeIn`, `float`, `pulse-glow`, skeleton shimmer, count-up. Respects `prefers-reduced-motion`.
- **Print stylesheet** included — flattens glass cards for "Save as PDF". Nice touch.
- **Knowledge base under `memory/`** — `DESIGN_SYSTEM.md`, `BRAND_IDENTITY.md`, `ARCHITECTURE.md`, `PRD.md`, `DESIGN_ANALYTICS.md`, `USER_JOURNEY.md`. These are the source of truth and should be referenced before any visual decision is made on mobile.

**Implication for mobile:** the design system is CSS-first (Tailwind + HSL variables). It maps cleanly to a Capacitor wrap (CSS unchanged) but **does not** map to React Native (which has no CSS engine). This is one of the strongest arguments in favor of Capacitor — see `MOBILE_STRATEGY.md`.

---

## 9. Tests

- 7 backend test files; no frontend tests (no Jest or Playwright config).
- Coverage focuses on the highest-risk areas: Swiss Ephemeris correctness, compatibility math, admin RBAC, error handling, CORS, and the transit cache. Good prioritization.
- CI workflow `.github/workflows/deploy-aws.yml` runs them.

---

## 10. Dead Code & Tech-Debt Hot Spots

- `backend/astro_engine.py` — never imported.
- `backend/payments.py` — never imported by `server.py`. The Stripe code in `server.py` reimplements it inline.
- `frontend/src/App.js:303-304` — `<Route path="*">` is outside `<Routes>` (placement bug).
- `server.py` is 127KB / ~2,900 lines, single file. Refactor by feature **before** the Telegram bot duplicates patterns from it.
- README claims "React 18" — `package.json` is on **React 19**.

---

## 11. Phase-1 Verdict

The platform is **functionally complete** as a web app. The math is right, the AI degrades gracefully, the auth is solid for v1, and the design system has real character. There are five issues that must be fixed before scaling to mobile + Telegram traffic:

1. Stripe webhook signature bypass (CRITICAL).
2. Missing token-expiry enforcement on email-verify and password-reset.
3. Pricing mismatch between `/api/pricing` and Stripe checkout.
4. Two payment code paths that could collide (`payments.py` vs `server.py`).
5. The `<Route path="*">` 404 placement bug.

Plus structural debt that pays back fast:
- Refactor `server.py` into `backend/routers/` per feature so the Telegram bot can import shared services without dragging in the FastAPI app.
- Extract `ai/` package (prompt builders + model client) to share with bot.
- Delete `astro_engine.py`.

These are tracked as Phase 4 commits.
