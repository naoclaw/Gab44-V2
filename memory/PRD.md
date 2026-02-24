# Gab44 V2 — Astrology & Numerology AI Coaching Platform

> **Mission:** Help people live measurably better lives through truthful astrological guidance.
> Every feature, every line of code, every design decision should ask: "Does this help people make better decisions?"

---

## 1. Vision & Mission

### Refined Mission Statement (from V3 Plan)
"Empower one billion people worldwide to discover their cosmic truth through accessible, accurate, and compassionate astrological guidance—available anytime, anywhere, in their native language."

### Core Values
- **Truthfulness over comfort** — Honest insights that serve growth
- **Accessibility** — Available to everyone, regardless of background
- **Holistic approach** — Astrology + Numerology + Gematria integration
- **Non-judgmental** — Compassionate guidance without moral superiority
- **Scientific accuracy** — Precise astronomical calculations (Swiss Ephemeris)

### User Personas
1. **Spiritual Seekers** — Looking for self-understanding and growth
2. **Astrology Enthusiasts** — Want daily guidance and chart analysis
3. **Life Coaches** — Use astrology for client guidance
4. **Entrepreneurs** — Seek timing guidance for business decisions

---

## 2. Architecture & Tech Stack

### Current Stack (V2 — implemented)
| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Tailwind CSS, shadcn/ui, Axios |
| Backend | FastAPI (Python 3.11), Motor (async MongoDB) |
| Database | MongoDB |
| AI | OpenAI GPT-4o (via emergentintegrations) |
| Auth | JWT + bcrypt |

### Target Stack (V2 complete — per main-branch README)
| Layer | Technology |
|-------|-----------|
| Frontend | React 18/19, Tailwind CSS, shadcn/ui, Axios |
| Backend | FastAPI (Python), Motor (async MongoDB) |
| Database | MongoDB |
| Ephemeris | pyswisseph (Swiss Ephemeris) |
| AI | OpenAI GPT-4o |
| Payments | Stripe (Checkout + Customer Portal + Webhooks) |
| Email | SendGrid (transactional + marketing) |
| Push | OneSignal Web Push |

### V3 Scale Architecture (future)
- Multi-region deployment (Americas, Europe, Asia, Africa)
- CDN for global asset delivery
- Redis caching layer
- Message queues for async operations
- PWA + Native mobile apps (Capacitor)
- Kubernetes container orchestration

---

## 3. Core Features

### 3.1 Natal Chart (Swiss Ephemeris)
- Sun, Moon, Rising + all planets, Lilith, Part of Fortune, True Node
- House placements via Placidus (Koch, Whole Sign optional)
- Major aspects (conjunction, opposition, trine, square, sextile) with applying/separating
- Minor aspects (quincunx, semi-sextile, sesquiquadrate)
- Chart patterns (Grand Trine, T-Square, Stellium, Yod, Kite)
- Retrograde markers
- Interactive SVG chart wheel with hover tooltips
- Export as PDF/PNG

### 3.2 Numerology
- Life Path Number
- Expression Number
- Soul Urge Number
- Personality Number
- Birthday Number
- Personal Year Number
- Master Numbers (11, 22, 33) preserved (Pythagorean method)
- First Name / Last Name analysis

### 3.3 Gematria
- Chaldean (Babylonian, A=1..Z=8)
- English Ordinal
- Interactive live demo on landing page
- Letter-by-letter breakdown
- Numerical significance and patterns

### 3.4 AI Cosmic Coach
- Conversational chat with full chart context injected
- Session history and management
- Tier-based daily message limits
- Quick prompt suggestions
- Personalized responses based on birth chart, numerology, and current transits
- Compassionate, non-judgmental tone

### 3.5 Daily AI Guidance
- Personalized based on natal chart (not just sun sign)
- Current planetary transits affecting the user
- Numerology Personal Year context
- Practical guidance for the day
- Affirmation or reflection prompt
- Push notification delivery (morning)
- 24-hour cache; graceful fallback

### 3.6 Transit Tracker
- Real-time planetary positions against natal chart
- Upcoming transits with real progress bars
- 45-entry interpretation library
- Strength and urgency calculations
- Transit alerts for significant events (Saturn return, Jupiter transit, retrogrades, eclipses)
- Action items per transit

### 3.7 Relationship Compatibility
- 5 relationship types: romantic, friendship, family, business, colleague
- Synastry analysis (inter-chart aspects)
- Composite charts (midpoint composite)
- Weighted scoring per relationship type
- Partner numerology comparison
- AI-generated interpretation
- Compatibility score and relationship dynamics report

### 3.8 Welcome Reports (AI-Generated)
- 5–10 page personalized report on chart creation
- Section-by-section breakdown (Sun, Moon, Rising, personal/social/outer planets, aspects, patterns)
- 3000+ word reports via GPT-4o with engineered prompts
- PDF export

### 3.9 Life Outcomes Tracking
- Track if guidance was helpful
- Follow-up system to check on recommended actions
- User-reported outcomes
- Measure: Life Improvement Rate, Action Taken Rate

### 3.10 Chart Management
- Create, edit, duplicate, delete charts
- Share chart via public link (revocable token)
- Favorite charts
- Side-by-side chart comparison

---

## 4. Pages & Routes

### Implemented (current branch)
| Route | Page | Auth Required |
|-------|------|:---:|
| `/` | LandingPage | No |
| `/auth` | AuthPage | No |
| `/pricing` | PricingPage | No |
| `/dashboard` | Dashboard | Yes |
| `/chat` | ChatPage | Yes |
| `/chart` | ChartPage | Yes |
| `/transits` | TransitsPage | Yes |
| `/settings` | SettingsPage | Yes |
| `/share` | ShareChartPage | Yes |
| `/numerology` | NumerologyPage | Yes |
| `/gematria` | GematriaPage | Yes |

### Target (per main-branch README — to be implemented)
| Route | Page | Auth Required | Status |
|-------|------|:---:|--------|
| `/` | LandingPage | No | ✅ Done |
| `/auth` | AuthPage | No | ✅ Done |
| `/pricing` | PricingPage | No | ✅ Done |
| `/dashboard` | Dashboard | Yes | ✅ Done |
| `/chat` | ChatPage | Yes | ✅ Done |
| `/chart` | ChartPage | Yes | ✅ Done |
| `/transits` | TransitsPage | Yes | ✅ Done |
| `/settings` | SettingsPage | Yes | ✅ Done |
| `/share` | ShareChartPage | Yes | ✅ Done |
| `/numerology` | NumerologyPage | Yes | ✅ Done |
| `/gematria` | GematriaPage | Yes | ✅ Done |
| `/compatibility` | CompatibilityPage | Yes | ❌ Not yet |
| `/admin` | AdminPage | Yes (admin) | ❌ Not yet |
| `/chart/:shareToken` | PublicChartPage | No | ❌ Not yet |
| `/verify-email` | VerifyEmailPage | No | ❌ Not yet |
| `/reset-password` | ResetPasswordPage | No | ❌ Not yet |

---

## 5. API Endpoints

### Implemented (current branch)
- `POST /api/auth/register` — User registration with birth details
- `POST /api/auth/login` — Login with JWT
- `GET  /api/auth/me` — Get current user
- `POST /api/chat` — Send chat message to AI coach
- `GET  /api/chat/history/{session_id}` — Get chat history
- `GET  /api/chat/sessions` — List chat sessions
- `GET  /api/chart/me` — Get/generate birth chart
- `GET  /api/transits/upcoming` — Get upcoming transits
- `GET  /api/guidance/daily` — Get daily guidance
- `GET  /api/pricing` — Get pricing plans
- `GET  /api/numerology/profile` — Get user's numerology profile (Life Path, Expression, Soul Urge, Personality, Birthday, Personal Year)
- `POST /api/gematria/calculate` — Calculate Chaldean + English Ordinal gematria for any text
- `GET  /api/health` — Health check

### Target (to be implemented)
- `POST /api/auth/verify-email` — Email verification
- `POST /api/auth/reset-password` — Password reset
- `PUT  /api/auth/profile` — Update user profile
- `PUT  /api/auth/preferences` — Update theme, language, timezone
- `POST /api/chart/create` — Create chart for another person
- `GET  /api/chart/{id}` — Get chart by ID
- `GET  /api/chart/share/{token}` — Get public chart by share token
- `POST /api/chart/{id}/share` — Generate share token
- `GET  /api/compatibility/analyze` — Synastry analysis
- `POST /api/compatibility/composite` — Composite chart
- `GET  /api/numerology/profile` — Get numerology profile
- `PUT  /api/numerology/profile` — Update numerology profile
- `POST /api/reports/generate` — Generate welcome report
- `GET  /api/reports/{chart_id}` — Get report for chart
- `POST /api/payments/checkout` — Create Stripe checkout session
- `POST /api/payments/webhook` — Stripe webhook handler
- `POST /api/payments/portal` — Customer portal session
- `POST /api/notifications/subscribe` — Push notification subscription
- `POST /api/admin/push-blast` — Admin daily push blast
- `GET  /api/admin/users` — Admin user list
- `GET  /api/admin/stats` — Admin dashboard stats

---

## 6. Design System

### Theme
- **Light Mode:** Warm cream (#FAF9F6) background, soft shadows, warm tones
- **Dark Mode:** Deep cosmic (#0F0F14 / #0A0E27) background, refined accents, starlight glow
- Theme toggle with localStorage persistence + system preference detection
- Smooth CSS transitions (300ms)

### Typography
- **Headings:** Cinzel (serif) — H1, H2, Hero text, tracking-tight
- **Body:** Manrope (sans) — All standard text, descriptions, chat
- **Data:** JetBrains Mono (mono) — Planetary degrees, time, coordinates
- **UI Elements:** Manrope (sans) — Buttons, navigation, inputs

### Color Palette (Cosmic Luxury)
```css
/* Light Theme */
--background: 40 30% 98%;
--foreground: 240 10% 15%;
--primary: 38 92% 50%;     /* Mystic Gold */
--muted: 40 20% 94%;

/* Dark Theme */
--background: 240 15% 6%;
--foreground: 40 20% 96%;
--primary: 42 92% 55%;     /* Mystic Gold */
--muted: 240 10% 14%;
```

Extended palette: `cosmic-void` (#050505), `cosmic-starlight` (#F8FAFC), `cosmic-gold` (#D4AF37), `cosmic-nebula` (#6366F1), `cosmic-silver` (#E2E8F0)

### Layout
- **Landing page:** Tetris Grid (Mode A) — Asymmetrical, overlapping elements
- **Dashboard:** Bento Grid (Mode B) — High density, gap-4, 100% height utilization
- Glass-morphism cards: `bg-black/40 backdrop-blur-xl border border-white/10`
- Generous spacing: p-8, p-12, p-24

### Visual Effects
- Noise overlay (opacity 0.03) on all solid backgrounds
- Glow effects on primary buttons
- Framer Motion animations: fade-ins (0.6s), staggered children
- Micro-animations on all interactive elements
- No universal `transition: all` (breaks transforms)

### Component Rules
- Components MUST use named exports (`export const ComponentName = ...`)
- Pages MUST use default exports (`export default function PageName() {...}`)
- Use `sonner` for toasts (located at `src/components/ui/sonner.jsx`)
- Use `lucide-react` for icons (no emoji characters for icons)
- All interactive elements must have `data-testid` attributes

---

## 7. Subscription Tiers

| Tier | Price | Key Features |
|------|-------|-------------|
| **Seeker** (Free) | $0/mo | Basic chart overview, daily short guidance, 1 compatibility reading, educational library |
| **Enthusiast** | $19.99/mo | Daily AI coaching, monthly detailed reports, unlimited compatibility, 30-day transit forecasts |
| **Advanced** | $49.99/mo | Advanced predictive tools, 90-day transit forecasts, chart pattern analysis, PDF export |
| **Professional** | $99/mo | Client management system, white-label reports, API access, priority support |

---

## 8. What's Been Implemented (February 24, 2026)

### Design System
- [x] Light theme — Warm cream (#FAF9F6), soft shadows
- [x] Dark theme — Deep cosmic (#0F0F14), refined accents
- [x] Theme toggle with localStorage persistence
- [x] System preference detection
- [x] Smooth theme transitions (300ms)
- [x] Glassmorphism header with scroll effect
- [x] Cinzel + Manrope typography
- [x] Mystic gold accent color
- [x] Improved line heights and letter spacing
- [x] Card lift hover effects
- [x] Focus states for accessibility

### Landing Page
- [x] Hero section with cosmic background and gradient text
- [x] Interactive sun sign calculator (timezone-safe UTC parsing)
- [x] Features section with card grid
- [x] AI Chat preview demonstration
- [x] Testimonials section
- [x] Pricing plans (all 4 tiers: Seeker, Enthusiast, Advanced, Professional)
- [x] FAQ accordion
- [x] CTA sections
- [x] Responsive navigation with theme toggle

### Authentication
- [x] Registration with birth details
- [x] Login with JWT tokens
- [x] Protected routes
- [x] Session persistence in localStorage
- [x] Split-screen design with cosmic imagery

### Dashboard
- [x] Bento grid layout
- [x] Daily energy/guidance display
- [x] Sun sign card
- [x] Active transits counter
- [x] Today's action items
- [x] Upcoming transits preview
- [x] Sidebar with theme toggle

### AI Coach Chat
- [x] Real-time AI coaching with GPT-4o
- [x] Conversation history persistence
- [x] Session management
- [x] Quick prompt suggestions
- [x] Personalized responses based on birth chart
- [x] Mobile-responsive sidebar (slide-in/out with overlay)

### Birth Chart
- [x] Big Three display (Sun, Moon, Rising)
- [x] All planetary positions with degrees
- [x] House cusps display
- [x] Major aspects listing
- [x] Chart patterns identification
- [ ] Swiss Ephemeris integration (currently simulated — priority upgrade)

### Transits
- [x] 90-day forecast display
- [x] Aspect type filtering
- [x] Action items per transit
- [x] Strength indicators
- [ ] Real transit calculations (currently simulated)

### Numerology
- [x] Life Path Number calculation (with Master Numbers 11, 22, 33)
- [x] Expression Number (full name, Pythagorean)
- [x] Soul Urge Number (vowels)
- [x] Personality Number (consonants)
- [x] Birthday Number
- [x] Personal Year Number
- [x] Letter-by-letter breakdown display
- [x] Full profile page with overview and details tabs

### Gematria
- [x] Chaldean (Babylonian) calculation engine
- [x] English Ordinal calculation engine
- [x] Letter-by-letter breakdown
- [x] Per-word value display
- [x] Numerical significance descriptions
- [x] Interactive calculator page with quick examples

---

## 9. Prioritized Backlog

### P0 — Critical (blocks launch)
- [ ] Swiss Ephemeris integration via `pyswisseph` for real chart calculations (`astro_calculator.py`)
- [ ] Stripe payment integration (Checkout + Customer Portal + Webhooks)
- [ ] Email verification and password reset (SendGrid)
- [x] Numerology engine (Life Path, Expression, Soul Urge, Personality, Birthday, Personal Year) — `numerology.py`
- [x] Gematria engine (Chaldean + English Ordinal) — `gematria.py`

### P1 — High (core product value)
- [ ] Relationship compatibility (synastry + composite charts, 5 relationship types)
- [ ] AI welcome report generation (5–10 page personalized report on chart creation)
- [ ] Real transit detection and progress bars (45-entry interpretation library)
- [ ] Push notifications via OneSignal (daily guidance, transit alerts)
- [ ] Daily/weekly/monthly AI-generated forecasts

### P2 — Medium (engagement & retention)
- [ ] Life outcomes tracking and follow-up system
- [ ] Educational content library (Astrology 101, glossary, blog/articles)
- [ ] Public chart sharing with revocable tokens (`PublicChartPage`)
- [ ] Admin dashboard (user management, push blast, stats)
- [ ] PDF report export
- [ ] User settings page (profile, preferences, subscription management)

### P3 — Low (scale & expansion)
- [ ] Progressions and solar returns
- [ ] Electional astrology (best dates for activities)
- [ ] Client management for Pro tier
- [ ] API access for developers
- [ ] White-label reports
- [ ] Internationalization (Phase 1: 10 languages)
- [ ] PWA with offline support + Capacitor native apps
- [ ] Mobile app (App Store + Play Store)

---

## 10. Backend Module Plan

### `server.py` (current)
All routes in a single FastAPI file. Handles auth, chat, charts (simulated), transits (simulated), guidance, pricing.

### `astro_calculator.py` (to be created)
Swiss Ephemeris integration + numerology + gematria calculations:
- `calculate_birth_chart(birth_date, birth_time, latitude, longitude)` — planetary positions, houses, aspects, patterns
- `calculate_numerology(name, birth_date)` — Life Path, Expression, Soul Urge, Personality, Birthday, Personal Year
- `calculate_gematria(name)` — Chaldean + English Ordinal with letter breakdown
- `detect_transits(natal_chart, date_range)` — scan for transit activations, strength, interpretations
- `calculate_compatibility(chart1, chart2, relationship_type)` — synastry aspects, composite, weighted scoring

### Reference Code (from V2 Package PDF)
The V2 package includes proven Python implementations:
- `gab44_chart_calculator.py` — Birth chart calculation engine with Swiss Ephemeris
- `gab44_transit_detector.py` — Transit pattern detection (found 409 activations in 90-day test)
- `gab44_ai_report_generator.py` — AI report generation (3000+ word reports)
- `gab44_v2_setup.py` — Database schema generator

---

## 11. Environment Variables

### Required
| Variable | Where | Description |
|----------|-------|-------------|
| `MONGO_URL` | backend | MongoDB connection string |
| `DB_NAME` | backend | Database name (e.g. `gab44`) |
| `JWT_SECRET` | backend | Random secret ≥ 32 chars for JWT signing |
| `REACT_APP_BACKEND_URL` | frontend | Backend API base URL |

### Optional (strongly recommended)
| Variable | Where | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | backend | GPT-4o for AI guidance, coach, compatibility |
| `EMERGENT_LLM_KEY` | backend | Emergent integrations LLM key |
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

## 12. Success Metrics

### Primary (Mission-Driven)
| Metric | Target | Description |
|--------|--------|-------------|
| Life Improvement Rate | >60% | % who report positive outcomes |
| Action Taken Rate | >30% | % who take recommended action |
| Retention (30-day) | >40% | % still active after 30 days |
| Engagement Depth | >5/month | Actions per user per month |
| NPS | >50 | Net Promoter Score |

### Secondary (Business)
| Metric | Target | Description |
|--------|--------|-------------|
| User Growth | 100/week by month 3 | New sign-ups per week |
| Conversion to Paid | >10% | % who upgrade from free |
| Churn Rate | <5% monthly | % who cancel subscription |
| DAU/MAU Ratio | >20% | Daily vs monthly active users (stickiness) |

### The Most Important Metric
**Are we helping people live measurably better lives?**

---

## 13. Implementation Roadmap (12-Week Plan from V2 Package)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1–2 | Foundation | Database + auth + project setup |
| 3–4 | Charts | Users can create and view real natal charts (Swiss Ephemeris) |
| 5–6 | AI Reports | Welcome reports generating successfully |
| 7–8 | Transits | Transit detection running daily |
| 9–10 | Notifications | Push notifications working end-to-end |
| 11 | Outcomes | Life outcomes tracking implemented |
| 12 | Launch | Production deployment + polish |

---

## 14. V3 Scale Vision (Long-Term — Road to 1.5 Billion Users)

### Year 1: Foundation (1M users)
- Implement light/dark themes, PWA, push notifications, Stripe payments
- Add internationalization (10 languages)
- Optimize for mobile devices

### Year 2: Growth (10M users)
- Transit forecasts, progressions, solar returns
- Community features (forums, groups)
- Educational content library
- Expand to 20 languages

### Year 3: Scale (100M users)
- B2B white-label solution
- AI chat for personalized guidance
- Gamification and achievements
- API for third-party integrations

### Year 4: Expansion (500M users)
- Voice-based chart readings
- Live astrologer consultations (marketplace)
- Wearables (Apple Watch)

### Year 5: 1.5 Billion Users
- Universal accessibility (50+ languages)
- AI-powered life coaching (beyond astrology)
- Integration with health and fitness apps
- Become the world's #1 astrology platform
- The stars are aligned. Let's begin.

---

## 15. Reference Documents

| Document | Description |
|----------|-------------|
| `Gab44.com_V2_Complete_Package.pdf` | V2 specifications, reference code, database schema, 12-week roadmap |
| `gab44_v3_complete_plan.pdf` | V3 mission evaluation, billion-user architecture, mobile strategy, monetization, 54-page plan |
| `design_guidelines.json` | Design system tokens, typography, colors, layout rules, component styles |
| `README.md` | Project setup, quick start, environment variables, deployment notes |

---

## 16. Key Architectural Decisions

### Why MongoDB?
- Flexible document model for varied chart data (JSONB-like)
- Async driver (Motor) integrates well with FastAPI
- Scales horizontally; good for rapid iteration

### Why Swiss Ephemeris?
- Astronomical accuracy: industry standard for astrology (arcsecond precision)
- Comprehensive: all planets, asteroids, house systems
- Open source (GPL or commercial license); 30+ years of development

### Why OpenAI GPT-4o?
- Best-in-class language model for personalized interpretations
- Reliable output with engineered prompts
- Cost-effective: ~$0.10 per 3000-word report

### Why React + Tailwind + shadcn/ui?
- Component reusability and large ecosystem
- Utility-first CSS for consistent design
- shadcn/ui provides accessible, customizable base components
- Great developer experience and tooling

---

## Test Results (Latest — February 24, 2026)
- Backend: 100% (12/12 tests passed)
- Frontend: Build passes (all pages compile, 0 errors)
- Theme system: Fully functional (light + dark)
- Auth flows: Working correctly
- AI Chat: Working correctly
- Mobile responsive: Dashboard + Chat sidebar ✓
- Pricing: All 4 tiers displayed correctly
- Sun sign calculator: Timezone-safe (UTC)
