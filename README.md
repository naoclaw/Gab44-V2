# Gab44 — Astrology & Numerology Platform

A full-stack astrology and numerology web app. Users get their natal chart, daily AI-powered guidance, relationship compatibility analysis, gematria, numerology profiles, and an AI cosmic coach — all built on Swiss Ephemeris for accurate planetary calculations.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS, shadcn/ui, Axios |
| Backend | FastAPI (Python), Motor (async MongoDB) |
| Database | MongoDB |
| Ephemeris | pyswisseph (Swiss Ephemeris) |
| AI | OpenAI GPT-4o |
| Payments | Stripe (Checkout + Customer Portal + Webhooks) |
| Email | SendGrid (transactional + marketing) |
| Push | OneSignal Web Push |

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)
- Swiss Ephemeris data files (optional — pyswisseph ships built-in data)

### 1. Clone & configure environment

```bash
git clone https://github.com/naoufac/Gab44-V2.git
cd Gab44-V2
```

Copy the environment template and fill in your keys:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

API will be live at **http://localhost:8001**  
Swagger docs at **http://localhost:8001/docs**

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

App will open at **http://localhost:3000**

---

## Environment Variables

See **`backend/.env.example`** and **`frontend/.env.example`** for the full list.

### Required (app won't start without these)

| Variable | Where | Description |
|----------|-------|-------------|
| `MONGO_URL` | backend | MongoDB connection string |
| `DB_NAME` | backend | Database name (e.g. `gab44`) |
| `JWT_SECRET` | backend | Random secret ≥ 32 chars for JWT signing |
| `REACT_APP_BACKEND_URL` | frontend | Backend API base URL |

### Optional but strongly recommended

| Variable | Where | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | backend | GPT-4o for AI guidance, coach, compatibility |
| `MAPBOX_ACCESS_TOKEN` | backend | Mapbox geocoding for birth city autocomplete (falls back to static 327-city database if not set) |
| `SENDGRID_API_KEY` | backend | Transactional + marketing email |
| `STRIPE_SECRET_KEY` | backend | Payments |
| `STRIPE_PUBLISHABLE_KEY` | backend | Stripe frontend key |
| `STRIPE_WEBHOOK_SECRET` | backend | Stripe webhook signature verification |
| `ONESIGNAL_APP_ID` | backend | Push notifications App ID |
| `ONESIGNAL_API_KEY` | backend | Push notifications API key |
| `ADMIN_EMAILS` | backend | Comma-separated emails granted admin access |
| `FRONTEND_URL` | backend | Full URL of the frontend (used in emails) |
| `CORS_ORIGINS` | backend | Comma-separated allowed origins (default: `*`) |

---

## Project Structure

```
Gab44-V2/
├── backend/
│   ├── server.py            # FastAPI app — all routes
│   ├── astro_calculator.py  # Swiss Ephemeris + inline numerology + gematria
│   ├── astro_engine.py      # Modular Swiss Ephemeris wrapper (natal charts + transits)
│   ├── numerology.py        # Pythagorean numerology engine (6 numbers, master number support)
│   ├── gematria.py          # Chaldean + English Ordinal gematria calculator
│   ├── cities.py            # 327-city geocoding database + Mapbox API hybrid
│   ├── payments.py          # Modular Stripe subscription management
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│       ├── test_swiss_ephemeris.py
│       ├── test_compatibility.py
│       └── test_admin_rbac.py
├── frontend/
│   ├── public/index.html    # OneSignal SDK loaded here
│   ├── src/
│   │   ├── App.js           # Router + AuthContext
│   │   ├── pages/           # One file per page
│   │   │   ├── LandingPage.jsx
│   │   │   ├── AuthPage.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ChartPage.jsx
│   │   │   ├── TransitsPage.jsx
│   │   │   ├── CompatibilityPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── FriendPage.jsx       # AI Friend
│   │   │   ├── NumerologyPage.jsx   # Full numerology profile
│   │   │   ├── GematriaPage.jsx     # Gematria calculator
│   │   │   ├── PricingPage.jsx
│   │   │   ├── SettingsPage.jsx
│   │   │   ├── AdminPage.jsx
│   │   │   ├── ShareChartPage.jsx
│   │   │   ├── PublicChartPage.jsx  # No auth required
│   │   │   ├── VerifyEmailPage.jsx
│   │   │   └── ResetPasswordPage.jsx
│   │   └── context/
│   │       └── ThemeContext.jsx
│   ├── .env.example
│   └── package.json
├── memory/
│   ├── PRD.md               # Full product requirements document
│   ├── ARCHITECTURE.md      # Website structure, navigation, routes
│   ├── DESIGN_SYSTEM.md     # CSS classes, colors, typography
│   ├── BRAND_IDENTITY.md    # Brand personality, voice, trust
│   └── DESIGN_ANALYTICS.md  # Deep design review
```

---

## Key Features

- **Natal Chart** — Sun, Moon, Rising + all planets, Lilith, Part of Fortune, True Node; house placements via Placidus; aspects with applying/separating; retrograde markers
- **Numerology** — Life Path, Expression, Soul Urge, Personality, Birthday, Personal Year, First Name, Last Name (Pythagorean; master numbers 11/22/33 preserved)
- **Gematria** — Chaldean (Babylonian, A=1..Z=8) + English Ordinal; interactive live demo on landing page
- **Daily AI Guidance** — OpenAI GPT-4o personalised to current transits, numerology Personal Year, and natal chart; 24-hour cache; graceful fallback
- **AI Cosmic Coach** — Conversational chat with full chart context injected; session history; tier-based daily message limits
- **AI Friend** — Warm, supportive cosmic companion with distinct personality; separate session management
- **Relationship Compatibility** — 5 relationship types (romantic, friendship, family, business, colleague); weighted scoring per type; partner numerology comparison; AI-generated interpretation
- **Transit Tracker** — Upcoming transits with real progress bars; 45-entry interpretation library
- **Stripe Payments** — Checkout, webhook, Customer Portal (manage/cancel); seeker/enthusiast/advanced/professional tiers
- **Email** — Verification, welcome, password reset, newsletter (4 typed SendGrid senders)
- **Push Notifications** — OneSignal Web Push; browser permission prompt; admin daily-blast endpoint
- **Public Chart Sharing** — Unique shareable URL; revocable token

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

---

## Deployment Notes

1. Set all env vars in your hosting platform (Railway, Render, Fly.io, etc.)
2. For Stripe webhooks: point `https://yourdomain.com/api/payments/webhook` to the FastAPI backend and set `STRIPE_WEBHOOK_SECRET`
3. For email verification links to work: set `FRONTEND_URL=https://yourdomain.com`
4. CORS: set `CORS_ORIGINS=https://yourdomain.com` (remove the `*` default in production)
5. MongoDB: ensure indexes are created on first startup (automatic via the `startup` event handler)

---

## License

Private / proprietary. All rights reserved.
