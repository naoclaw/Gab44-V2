# Gab44 V2 — Architecture & Navigation

> **Purpose**: Any AI reading this file knows exactly how the platform is structured, how pages connect, how users navigate, and where every piece of code lives.

---

## 1. Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | React 19 + Tailwind CSS + Shadcn UI | CRA with craco override |
| **Backend** | FastAPI + Python 3.11 | Single `server.py` monolith |
| **Database** | MongoDB (Motor async driver) | Collections listed below |
| **AI** | OpenAI GPT-4o (direct SDK) | Two personas: Coach + Saoul |
| **Astrology** | Swiss Ephemeris (pyswisseph) | Accurate planetary calculations |
| **Auth** | JWT + bcrypt | Token in localStorage |
| **Payments** | Stripe (Checkout + Webhooks + Portal) | Inline price_data |
| **Email** | SendGrid (4 sender addresses) | noreply@, verify@, support@, marketing@ |
| **Push** | OneSignal Web SDK | player_id stored on user |
| **Geocoding** | Static city dict + Nominatim fallback | LRU-cached |

---

## 2. Frontend File Structure

```
frontend/src/
├── App.js                    # Routes + AuthProvider + ProtectedRoute/AdminRoute
├── index.js                  # React root render
├── index.css                 # Full design system (themes, glass effects, animations)
├── context/
│   ├── ThemeContext.jsx       # { theme, toggleTheme } — stored in localStorage "gab44_theme"
│   └── ReadingModeContext.jsx # { readingMode, fontSize } — stored in localStorage
├── components/ui/            # 44 Shadcn/ui components (button, input, card, dialog, etc.)
├── lib/
│   └── utils.js              # cn() classname merger + parseApiError()
├── hooks/
│   └── use-toast.js
└── pages/
    ├── LandingPage.jsx       # Public marketing page (12 sections)
    ├── AuthPage.jsx           # Login / Register with birth details
    ├── Dashboard.jsx          # Sidebar + bento grid overview
    ├── ChatPage.jsx           # AI Coach chat interface
    ├── FriendPage.jsx         # AI Friend (Saoul) chat interface
    ├── ChartPage.jsx          # Full natal chart display
    ├── CompatibilityPage.jsx  # Synastry reports
    ├── TransitsPage.jsx       # Current transits with progress
    ├── PricingPage.jsx        # Stripe checkout tiers
    ├── SettingsPage.jsx       # Profile, notifications, subscription
    ├── ShareChartPage.jsx     # Generate public chart link
    ├── PublicChartPage.jsx    # Unauthenticated chart view
    ├── AdminPage.jsx          # Admin dashboard
    ├── VerifyEmailPage.jsx    # Email verification landing
    └── ResetPasswordPage.jsx  # Password reset landing
```

---

## 3. Provider Hierarchy

Every page is wrapped in this context tree:

```
ThemeProvider              ← dark/light mode, persists to localStorage
  └── ReadingModeProvider  ← font size + reading mode for chat pages
      └── AuthProvider     ← { user, token, login, register, logout, updateUser }
          └── BrowserRouter
              └── Routes
          └── Toaster (sonner, position: top-right)
```

**AuthProvider** (defined in App.js):
- On mount: reads `gab44_token` from localStorage → calls `GET /api/auth/me` to verify
- Exposes: `user` object, `token` string, `login()`, `register()`, `logout()`, `updateUser()`
- `user` contains: `name`, `email`, `sun_sign`, `subscription_tier`, `is_admin`, `birth_*` fields

---

## 4. Route Map

### Public Routes (no auth required)

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | LandingPage | Marketing, features, pricing, gematria demo |
| `/auth` | AuthPage | Login or register (`?mode=register` for signup) |
| `/pricing` | PricingPage | Detailed pricing with Stripe checkout |
| `/verify-email` | VerifyEmailPage | Email verification callback (`?token=`) |
| `/reset-password` | ResetPasswordPage | Password reset callback (`?token=`) |
| `/chart/public/:token` | PublicChartPage | Shared chart view (no login needed) |

### Protected Routes (requires valid JWT)

| Path | Component | Purpose |
|------|-----------|---------|
| `/dashboard` | Dashboard | Main hub — daily guidance, transits, numerology, quick actions |
| `/chat` | ChatPage | AI Coach conversations (session-based) |
| `/friend` | FriendPage | AI Friend (Saoul) conversations |
| `/chart` | ChartPage | Full natal chart — planets, houses, aspects, patterns, numerology, gematria |
| `/transits` | TransitsPage | Current outer planet transits with progress bars |
| `/settings` | SettingsPage | Profile edit, notifications, subscription management |
| `/share` | ShareChartPage | Generate/manage public chart sharing link |
| `/compatibility` | CompatibilityPage | Synastry reports with partner birth data |

### Admin Routes (requires `is_admin === true`)

| Path | Component | Purpose |
|------|-----------|---------|
| `/admin` | AdminPage | User management, stats, email blasts, newsletters, contacts |

---

## 5. Dashboard Sidebar Navigation

The sidebar is defined in `Dashboard.jsx`. It lists all inner pages:

| Order | ID | Icon | Label | Route |
|-------|-----|------|-------|-------|
| 1 | overview | BarChart3 | Overview | (internal — stays on dashboard) |
| 2 | chat | MessageCircle | AI Coach | `/chat` |
| 3 | friend | Coffee | AI Friend | `/friend` |
| 4 | chart | Sun | Birth Chart | `/chart` |
| 5 | compatibility | Heart | Compatibility | `/compatibility` |
| 6 | transits | Calendar | Transits | `/transits` |
| 7 | share | Share2 | Share Chart | `/share` |
| 8 | settings | Settings | Settings | `/settings` |
| 9* | admin | Shield | Admin | `/admin` |

*Admin item only shown if `user.is_admin === true`

**Sidebar bottom section**: Theme toggle, user profile card (avatar + name + sun sign + tier badge), Sign Out button.

**Mobile**: Sidebar collapses into a slide-in drawer triggered by a hamburger button in `MobileHeader`.

---

## 6. Landing Page Section Order

The landing page renders these sections top-to-bottom:

```
1.  Navigation       — Sticky glass header with links + Sign In / Get Started
2.  HeroSection      — "The Stars Know You" + Sun Sign calculator + stats
3.  GematriaSection  — Interactive Chaldean gematria demo (type any word)
4.  FeaturesSection  — AI Coaching, Deep Analysis, Spiritual Growth + Life Areas
5.  ChatPreview      — Coach vs Saoul side-by-side chat previews
6.  TestimonialsSection — 3 user testimonials
7.  PricingSection   — Seeker (Free) / Enthusiast ($9.99) / Advanced ($29.99)
8.  FAQSection       — 4 questions in accordion
9.  CTASection       — "Your Chart Is Waiting" + privacy badge
10. NewsletterSection — Email capture form
11. ContactSection   — Contact form (name, email, subject, message)
12. Footer           — Logo, copyright, Privacy/Terms/Contact links
```

---

## 7. Backend Structure

### File Organization

```
backend/
├── server.py           # Main FastAPI app (monolith — all routes + models + helpers)
├── astro_calculator.py # Swiss Ephemeris calculations (planetary positions, houses, aspects)
├── requirements.txt    # Python dependencies
├── .env.example        # All required environment variables
└── tests/              # Backend test files
```

### server.py Section Map

The backend is organized with `# ============== Section ==============` comment headers:

1. **Imports & Config** — FastAPI app, CORS, environment variables
2. **Models** — Pydantic models for request/response (User, Chat, Chart, etc.)
3. **Compatibility Models** — Partner data, synastry models
4. **Payment + Notification Models** — Stripe, OneSignal models
5. **Auth Helpers** — JWT create/verify, password hashing, get_current_user dependency
6. **Email Helper** — SendGrid integration with branded HTML templates
7. **Astrology Helpers** — Chart calculation orchestration
8. **Compatibility Calculations** — Synastry scoring, AI analysis
9. **AI Coach** — `get_ai_coach_response()` — system prompt with full chart context
10. **AI Friend (Saoul)** — `get_ai_friend_response()` — warm, casual system prompt
11. **Auth Routes** — register, login, verify-email, forgot/reset password, profile
12. **Chat Routes** — POST chat, GET history/sessions, DELETE session
13. **AI Friend Routes** — POST friend/chat, GET history/sessions, DELETE session
14. **Birth Chart Routes** — GET chart/me, POST/DELETE chart/share, GET public chart
15. **Transit Routes** — GET upcoming transits with real positions
16. **Daily Guidance** — GET guidance/daily (24h cached, OpenAI-generated)
17. **Compatibility Routes** — POST analyze, GET reports
18. **Pricing/Subscription** — GET pricing (returns tier details)
19. **OneSignal Helper** — Push notification sending
20. **Payment Routes** — Stripe checkout, webhook, customer portal
21. **Notification Routes** — Device registration, send daily (admin)
22. **Newsletter & Contact** — Subscribe, contact form with auto-reply
23. **Health Check** — GET /health
24. **Admin Routes** — Stats, user management, email blast, newsletter/contact lists
25. **Startup** — MongoDB index creation on app start

### MongoDB Collections

| Collection | Purpose | Key Indexes |
|-----------|---------|-------------|
| `users` | User accounts | `email` (unique), `stripe_customer_id` (sparse) |
| `birth_charts` | Natal chart data | `user_id` (unique), `share_token` (sparse) |
| `chat_messages` | AI Coach conversations | `user_id`, `session_id`, `(user_id, session_id)` |
| `friend_messages` | AI Friend (Saoul) conversations | `user_id`, `session_id`, `(user_id, session_id)` |
| `compatibility_reports` | Synastry analyses | `user_id` |
| `newsletter_subscribers` | Email list | `email` (unique) |
| `contact_messages` | Support tickets | (auto) |

---

## 8. User Flow Logic

### Registration → First Chart

```
1. User clicks "Get Started" on landing page
2. → /auth?mode=register
3. User enters: name, email, password, birth_name, birth_date, birth_time, birth_city
4. Backend: creates user (seeker tier), sends verification email
5. → Redirect to /dashboard
6. Dashboard fetches: daily guidance, transits, numerology
7. User clicks "Birth Chart" in sidebar → /chart
8. ChartPage calls GET /api/chart/me (calculates on first visit, caches in MongoDB)
9. Full chart displayed: planets, houses, aspects, patterns, numerology, gematria
```

### Daily Return Flow

```
1. User opens gab44.com → already logged in (JWT in localStorage)
2. → /dashboard
3. Dashboard shows: personalized greeting, daily energy, focus areas, action items
4. User can: Ask AI Coach, Talk to Saoul, Check transits, View chart
```

### Subscription Upgrade

```
1. User clicks "Start Free Trial" on pricing
2. → POST /api/payments/create-checkout-session { tier: "enthusiast" }
3. → Redirect to Stripe Checkout
4. Stripe webhook: checkout.session.completed → upgrade user tier in MongoDB
5. → Redirect back to /dashboard?subscription=success
6. Dashboard shows success toast
```

### AI Chat (Coach or Friend)

```
1. User navigates to /chat (Coach) or /friend (Saoul)
2. Left panel: session list (previous conversations)
3. Right panel: chat messages
4. User types message → POST /api/chat or /api/friend/chat
5. Backend: checks daily message limit → builds system prompt with chart context → calls GPT-4o
6. Response streamed back, saved to MongoDB
7. Both personas share same tier limits (seeker=10/day, enthusiast=100/day, advanced/pro=unlimited)
```

---

## 9. Environment Variables

All required env vars are documented in `backend/.env.example`:

| Variable | Purpose |
|----------|---------|
| `MONGODB_URL` | MongoDB connection string |
| `JWT_SECRET` | JWT signing key |
| `OPENAI_API_KEY` | GPT-4o access |
| `STRIPE_SECRET_KEY` | Stripe payments |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook verification |
| `SENDGRID_API_KEY` | Email sending |
| `ONESIGNAL_APP_ID` | Push notifications |
| `ONESIGNAL_API_KEY` | Push notifications |
| `ADMIN_EMAILS` | Comma-separated admin email list |
| `FRONTEND_URL` | Frontend URL for CORS + email links |
| `BACKEND_URL` | Backend URL for self-reference |

---

*This file maps the complete platform structure. For design system details, see `DESIGN_SYSTEM.md`. For brand identity, see `BRAND_IDENTITY.md`. For feature inventory, see `PRD.md`.*
