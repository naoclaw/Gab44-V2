# Gab44 V2 - Astrology AI Coaching Platform

## Architecture & Tech Stack
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + Python 3.11
- **Database**: MongoDB
- **AI Integration**: OpenAI GPT-4o (direct SDK)
- **Astrology Calculations**: Swiss Ephemeris (pyswisseph)
- **Authentication**: JWT-based with bcrypt password hashing
- **Authorization**: Role-Based Access Control (RBAC)
- **Payments**: Stripe (Checkout, Webhooks, Customer Portal)
- **Email**: SendGrid with 4 typed sender addresses
- **Push Notifications**: OneSignal Web SDK
- **Geocoding**: Static city dict + Nominatim (OpenStreetMap) fallback

## What's Implemented

### Auth & User Management
- [x] User registration with birth details (defaults to `seeker` free tier)
- [x] `birth_name` field (legal name for numerology accuracy)
- [x] JWT login / logout
- [x] Email verification on registration (SendGrid, 48h expiry)
- [x] Welcome email on verification
- [x] Forgot password / reset password flow (1h token expiry)
- [x] Resend verification email
- [x] PUT /api/auth/me — update profile (name, birth data, birth_name, notifications)
- [x] `is_admin` in UserProfile (returned by login, register, and /auth/me)
- [x] Password complexity validation (min 8 chars, letter + digit/special)

### AI Coaching
- [x] GPT-4o AI coaching chat (session-based, history aware)
- [x] System prompt enriched with full natal planets, top 5 aspects, and all numerology numbers
- [x] Chat tier enforcement: seeker=10 msg/day, enthusiast=100/day, advanced/professional=unlimited
- [x] Delete chat session
- [x] AI-powered daily guidance (OpenAI, 24h server-side cache, fallback text)
- [x] Daily guidance enriched with Personal Year + Life Path numerology

### AI Friend (Saoul)
- [x] Separate AI friend persona — warm, casual, present (not a coach, not a therapist)
- [x] Own system prompt: matches user energy, no unsolicited advice, genuine human warmth
- [x] Separate `friend_messages` MongoDB collection (isolated from coach messages)
- [x] Session management (create, list, load history, delete)
- [x] Same tier-based daily message limits as AI Coach
- [x] Dedicated FriendPage UI with rose/warm accent color palette
- [x] Dashboard sidebar navigation ("AI Friend" with Coffee icon)

### Astrology Engine (Swiss Ephemeris)
- [x] Accurate planetary positions (Sun through Pluto)
- [x] Black Moon Lilith (Mean Apogee, ⚸)
- [x] Part of Fortune / Lot of Fortune (⊕, day/night formula)
- [x] Lunar Nodes (True Node — not Mean Node)
- [x] Chiron (when ephemeris files available)
- [x] House cusps (Placidus system)
- [x] Ascendant (Rising Sign) and Midheaven
- [x] Aspect calculations with applying/separating via speed projection
- [x] Chart pattern detection (Grand Trine, T-Square, Stellium, etc.)
- [x] Real transits from current planetary positions with progress tracking
- [x] Birth time timezone conversion (timezonefinder + zoneinfo)
- [x] Nominatim geocoding fallback for unknown cities (LRU-cached successes)
- [x] Sun sign via Swiss Ephemeris (replaced lookup table)

### Pythagorean Numerology Engine
- [x] Life Path (birth date, master numbers 11/22/33 preserved)
- [x] Expression / Destiny (full name)
- [x] Soul Urge / Heart's Desire (vowels)
- [x] Personality (consonants)
- [x] Birthday Number
- [x] Personal Year Number (adjusts for birthday not yet passed)
- [x] First Name & Family Name numbers
- [x] All numbers include keyword + theme text

### Gematria Engine (NEW)
- [x] Chaldean cipher (ancient Babylonian, values 1–8) — directly connected to astrology's roots
- [x] English Ordinal (A=1…Z=26)
- [x] Both totals and reductions with number meanings
- [x] Interactive input on Chart page — analyse any name or word in real time
- [x] Letter-by-letter Chaldean breakdown display

### Compatibility (Synastry)
- [x] Swiss Ephemeris charts for both partners
- [x] Element and modality compatibility scoring
- [x] Synastry aspects calculation
- [x] AI-powered relationship analysis
- [x] Report cards and detailed view

### Payments (Stripe)
- [x] POST /api/payments/create-checkout-session — inline price_data, reuse/create Stripe Customer
- [x] POST /api/payments/webhook — checkout.session.completed → upgrade tier; subscription.deleted → downgrade
- [x] POST /api/payments/portal — Stripe Customer Portal (manage/cancel)
- [x] PricingPage — CTAs start checkout; "Current Plan" badge; spinner state
- [x] Dashboard detects ?subscription=success, shows toast
- [x] SettingsPage — "Manage Subscription" button for paid users

### Email (SendGrid — 4 typed senders)
- [x] `noreply@` — transactional (password reset)
- [x] `verify@` — email verification + welcome
- [x] `support@` — contact form auto-reply + support replies
- [x] `marketing@` — newsletter confirmation + promotional blasts
- [x] Branded dark-theme HTML templates for all email types

### Push Notifications (OneSignal)
- [x] Web SDK in index.html (App ID: e143a4a3-a485-40a8-b665-31d21a1b1de7)
- [x] POST /api/notifications/register-device — stores player_id on user
- [x] POST /api/notifications/send-daily (admin) — sends push via OneSignal REST API
- [x] SettingsPage — push toggle requests browser permission, registers device

### Newsletter & Contact
- [x] POST /api/subscribe — deduplicates, sends SendGrid confirmation
- [x] POST /api/contact — stores ticket, emails support@, sends auto-reply with ticket ID
- [x] Newsletter capture widget in LandingPage
- [x] Contact form section in LandingPage
- [x] Contact link in nav bar

### Admin
- [x] Admin role via ADMIN_EMAILS env var or database field
- [x] Admin RBAC (grant/revoke admin)
- [x] User management (list, change tier, change role)
- [x] Platform stats dashboard
- [x] Email blast to all users or tier-filtered (BackgroundTasks, 10k batches)
- [x] Newsletter subscriber list
- [x] Contact message list

### Frontend Pages
- [x] LandingPage — Hero, Features, Testimonials, Pricing, FAQ, Newsletter, Contact
- [x] AuthPage — Login/Register (birth_name field, password hint)
- [x] Dashboard — Bento grid, daily guidance, transits, numerology tiles
- [x] ChatPage — AI coaching, session management, tier limit toast
- [x] FriendPage — AI friend (Saoul), warm rose accent, separate sessions
- [x] ChartPage — Planets (with Lilith, PoF, ℞ badge), Houses, Aspects, Patterns, Numerology, Gematria
- [x] CompatibilityPage — Synastry reports
- [x] TransitsPage — Real outer planet transits with real progress bars
- [x] PricingPage — Stripe checkout integration
- [x] SettingsPage — Profile edit, birth_name, notifications, subscription management
- [x] ShareChartPage — Real public URL generation
- [x] PublicChartPage — Unauthenticated public chart view
- [x] VerifyEmailPage — Email verification landing
- [x] ResetPasswordPage — Password reset landing
- [x] AdminPage — Full admin dashboard with email blast UI

### Infrastructure
- [x] MongoDB indexes: email (unique), user_id, session_id, share_token (sparse), stripe_customer_id (sparse), newsletter_subscribers.email (unique)
- [x] Startup index creation
- [x] All Emergent branding removed (plugins, scripts, iframe, badge, PostHog, .emergent/)
- [x] backend/.env.example with all required variables documented
- [x] Print / Save as PDF from ChartPage

## API Endpoints

### Auth
- POST /api/auth/register
- POST /api/auth/login
- GET  /api/auth/me
- PUT  /api/auth/me
- GET  /api/auth/verify-email?token=
- POST /api/auth/resend-verification
- POST /api/auth/forgot-password
- POST /api/auth/reset-password

### Core
- POST /api/chat
- GET  /api/chat/history/{session_id}
- GET  /api/chat/sessions
- DELETE /api/chat/session/{session_id}
- POST /api/friend/chat
- GET  /api/friend/history/{session_id}
- GET  /api/friend/sessions
- DELETE /api/friend/session/{session_id}
- GET  /api/chart/me?recalculate=bool
- POST /api/chart/share
- DELETE /api/chart/share
- GET  /api/chart/public/{share_token}
- GET  /api/numerology/me
- GET  /api/transits/upcoming
- GET  /api/guidance/daily
- GET  /api/pricing

### Compatibility
- POST /api/compatibility/analyze
- GET  /api/compatibility/reports
- GET  /api/compatibility/reports/{id}

### Payments
- POST /api/payments/create-checkout-session
- POST /api/payments/portal
- POST /api/payments/webhook

### Notifications
- POST /api/notifications/register-device
- POST /api/notifications/send-daily (admin)

### Newsletter & Contact
- POST /api/subscribe
- POST /api/contact

### Admin (Protected)
- GET  /api/admin/stats
- GET  /api/admin/users
- PUT  /api/admin/users/{user_id}/tier
- PUT  /api/admin/users/{user_id}/role
- GET  /api/admin/admins
- GET  /api/admin/newsletter-subscribers
- GET  /api/admin/contact-messages
- POST /api/admin/send-email-blast

## Admin Credentials
- **Email**: nchobah@gmail.com
- **ADMIN_EMAILS env var**: nchobah@gmail.com

## Subscription Tiers
| Tier | Price | Chat Messages/day | Features |
|------|-------|-------------------|----------|
| seeker | Free | 10 | Basic chart, daily guidance |
| enthusiast | $9.99/mo | 100 | + Compatibility reports |
| advanced | $29.99/mo | Unlimited | + Transits, full numerology |
| professional | $79.99/mo | Unlimited | + Priority support, API access |
