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
| `EMAIL_NOREPLY` | backend | "From" address for automated system emails |
| `EMAIL_VERIFY` | backend | "From" address for sign-up / verification emails |
| `EMAIL_SUPPORT` | backend | "From" address for support replies |
| `EMAIL_MARKETING` | backend | "From" address for promotions & newsletters |
| `STRIPE_SECRET_KEY` | backend | Payments — server-side Stripe key |
| `STRIPE_PUBLISHABLE_KEY` | backend | Stripe frontend key (informational, unused server-side) |
| `STRIPE_WEBHOOK_SECRET` | backend | Stripe webhook signature verification |
| `ONESIGNAL_APP_ID` | backend | Push notifications App ID |
| `ONESIGNAL_API_KEY` | backend | Push notifications REST API key |
| `REACT_APP_ONESIGNAL_APP_ID` | frontend | Same OneSignal App ID — injected into `index.html` at build time |
| `ADMIN_EMAILS` | backend | Comma-separated emails granted admin access |
| `FRONTEND_URL` | backend | Full URL of the frontend (used in email links) |
| `CORS_ORIGINS` | backend | Comma-separated allowed origins (default: `*`) |

---

## Project Structure

```
Gab44-V2/
├── backend/
│   ├── server.py            # FastAPI app — all routes (2,600+ lines)
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
│       ├── test_admin_rbac.py
│       └── test_api_integration.py
├── frontend/
│   ├── public/index.html    # OneSignal SDK loaded here
│   ├── src/
│   │   ├── App.js           # Router + AuthContext (17 routes)
│   │   ├── pages/           # One file per page (17 pages)
│   │   │   ├── LandingPage.jsx
│   │   │   ├── AuthPage.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ChartPage.jsx
│   │   │   ├── TransitsPage.jsx
│   │   │   ├── CompatibilityPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── FriendPage.jsx       # AI Friend (Saoul)
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
├── memory/                          # Platform knowledge base
│   ├── PRD.md               # Product requirements + API reference
│   ├── ARCHITECTURE.md      # Website structure, navigation, routes
│   ├── DESIGN_SYSTEM.md     # CSS classes, colors, typography
│   ├── BRAND_IDENTITY.md    # Brand personality, voice, trust
│   └── DESIGN_ANALYTICS.md  # Deep design review
├── design_guidelines.json   # Design system tokens & rules
├── README.md                # This file
└── *.pdf                    # V2 specs + V3 vision docs
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

## AWS Deployment

The CI/CD pipeline in `.github/workflows/deploy-aws.yml` automatically deploys the application to AWS on every push to `main`:

- **Frontend** → S3 static website + CloudFront CDN
- **Backend** → AWS Elastic Beanstalk (Python 3.11 + uvicorn)

### Architecture

```
Browser → CloudFront (CDN) → S3 (React SPA)
                           → Elastic Beanstalk (FastAPI) → MongoDB Atlas
```

### Prerequisites

| AWS Resource | Description |
|---|---|
| S3 bucket (frontend) | Hosts the built React static files. Enable static website hosting. |
| S3 bucket (EB artifacts) | Stores Elastic Beanstalk deployment ZIPs. |
| CloudFront distribution | CDN in front of the frontend S3 bucket. Set the origin to the S3 website endpoint and configure a default root object of `index.html`. Add a custom error response for 403/404 → `index.html` (200) for client-side routing. |
| Elastic Beanstalk application + environment | Python 3.11 platform. The `backend/Procfile` starts uvicorn. |
| IAM user | Needs `elasticbeanstalk:*`, `s3:*` on the two buckets, and `cloudfront:CreateInvalidation`. |

### GitHub Secrets

Add the following secrets in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |
| `EB_APP_NAME` | Elastic Beanstalk application name |
| `EB_ENV_NAME` | Elastic Beanstalk environment name |
| `EB_S3_BUCKET` | S3 bucket for EB deployment artifacts |
| `FRONTEND_S3_BUCKET` | S3 bucket for the React static build |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID |
| `REACT_APP_BACKEND_URL` | Public URL of the EB backend (no trailing slash) |
| `REACT_APP_ONESIGNAL_APP_ID` | OneSignal App ID (optional) |
| `MONGO_URL` | MongoDB Atlas connection string (used by tests in CI) |
| `DB_NAME` | MongoDB database name (used by tests in CI) |
| `JWT_SECRET` | JWT signing secret (used by tests in CI) |

### Elastic Beanstalk setup

1. Create an EB application and a **Python 3.11** environment.
2. The `backend/Procfile` starts the server:
   ```
   web: uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
   ```
3. Set the environment variables listed in `backend/.env.example` under **Configuration → Software → Environment properties**.
4. The `backend/.ebextensions/01_python.config` and `backend/.platform/nginx/conf.d/proxy_timeout.conf` are bundled in the deployment ZIP and applied automatically.

### Stripe webhook

After the EB environment is up:

1. In Stripe Dashboard → Developers → Webhooks, add endpoint: `https://api.yourdomain.com/api/payments/webhook`
2. Copy the Signing Secret and set `STRIPE_WEBHOOK_SECRET` in the EB environment properties.

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| EB deploy fails on startup | Check environment properties — `MONGO_URL`, `DB_NAME`, `JWT_SECRET` must be set |
| Frontend routing returns 403 | Add a CloudFront custom error response: 403 → `/index.html` (200) |
| CORS errors in the browser | Set `CORS_ORIGINS` in EB to the CloudFront domain (no trailing slash) |
| Stripe webhooks rejected | Verify `STRIPE_WEBHOOK_SECRET` matches the Stripe signing secret |

---

## Deployment Notes

1. Set all env vars in your hosting platform (Railway, Render, Fly.io, AWS, etc.)
2. For Stripe webhooks: point `https://yourdomain.com/api/payments/webhook` to the FastAPI backend and set `STRIPE_WEBHOOK_SECRET`
3. For email verification links to work: set `FRONTEND_URL=https://yourdomain.com`
4. CORS: set `CORS_ORIGINS=https://yourdomain.com` (remove the `*` default in production)
5. MongoDB: ensure indexes are created on first startup (automatic via the `startup` event handler)

---

## Railway Deployment

This repo is structured as a **monorepo** — deploy each service separately in Railway.

> **First time on Railway? Follow the steps in order — the backend won't start
> until MongoDB is provisioned and all required env vars are set.**

### Step 1 — Add MongoDB to your Railway project

Before deploying the backend, add a database:

1. In your Railway **project**, click **+ New** → **Database** → **Add MongoDB**.
2. Railway provisions a MongoDB instance and automatically makes a `MONGO_URL`
   variable available to any service in the same project.
3. You still need to set `DB_NAME = gab44` manually (see Step 2 below).

Alternatively, use **MongoDB Atlas**: create a free M0 cluster, copy the
connection string, and set it as `MONGO_URL` in the backend service variables.

---

### Step 2 — Deploy the backend service

1. In Railway, click **+ New** → **GitHub Repo** → pick this repository.
2. Set **Root Directory** → `backend`.
3. Railway will use `backend/railway.toml` (start command, health-check) and
   `backend/nixpacks.toml` (Python 3.11, build deps) automatically.
4. Add the following **service variables** (Settings → Variables):

| Variable | Required | Value / Description |
|----------|----------|---------------------|
| `MONGO_URL` | ✅ | Injected automatically if you added Railway MongoDB; otherwise paste your Atlas URI |
| `DB_NAME` | ✅ | `gab44` |
| `JWT_SECRET` | ✅ | Long random secret — run `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FRONTEND_URL` | ✅ | Full URL of the deployed frontend (e.g. `https://gab44.up.railway.app`) |
| `CORS_ORIGINS` | ✅ | Same as `FRONTEND_URL` |
| `OPENAI_API_KEY` | optional | GPT-4o key |
| `SENDGRID_API_KEY` | optional | SendGrid key |
| `EMAIL_NOREPLY` / `EMAIL_VERIFY` / `EMAIL_SUPPORT` / `EMAIL_MARKETING` | optional | Verified SendGrid senders |
| `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` / `STRIPE_PUBLISHABLE_KEY` | optional | Stripe keys |
| `ONESIGNAL_APP_ID` / `ONESIGNAL_API_KEY` | optional | OneSignal keys |

5. Click **Deploy**. Check the deploy logs — if any required variable is missing
   you will see a clear error message listing exactly which ones to add.

---

### Step 3 — Deploy the frontend service

1. In Railway, click **+ New** → **GitHub Repo** → same repository.
2. Set **Root Directory** → `frontend`.
3. Railway will use `frontend/railway.toml` automatically.
4. Add service variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `REACT_APP_BACKEND_URL` | ✅ | Public URL of the deployed backend service (no trailing slash) |
| `REACT_APP_ONESIGNAL_APP_ID` | optional | OneSignal App ID |

---

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Backend deploy fails with `EnvironmentError: Missing required environment variables` | `MONGO_URL`, `DB_NAME`, or `JWT_SECRET` not set | Set them in the backend service variables (Step 2) |
| `MONGO_URL` is not injected automatically | MongoDB database not added to the Railway project | Add it via **+ New → Database → MongoDB** first |
| Frontend shows network errors / can't reach API | `REACT_APP_BACKEND_URL` wrong or not set | Set it to the public URL of your backend Railway service |

---

## License

Private / proprietary. All rights reserved.
