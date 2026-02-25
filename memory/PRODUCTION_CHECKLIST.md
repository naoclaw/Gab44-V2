# Gab44 V2 — Production Readiness Checklist

> **Purpose**: Technical evaluation covering caching, performance, security, and server deployment.  
> Reference this document before every production release.

---

## 1. Caching

### What's Already Implemented ✅

| Cache | Location | TTL | Notes |
|-------|----------|-----|-------|
| Birth chart (natal) | `birth_charts` MongoDB collection | Permanent (recalculate=true to bust) | Computed once on first `GET /api/chart/me`, stored forever |
| Daily guidance | `daily_guidance` MongoDB collection | 24 hours (keyed on `user_id` + `date`) | One OpenAI call per user per day |
| Numerology profile | `numerology_profiles` MongoDB collection | Permanent | Full 6-number Pythagorean profile |
| Nominatim geocoding | LRU in-process cache (`functools.lru_cache`) | Process lifetime | Cities not in the 327-city static list |
| Transit calculations | Calculated on-demand | None | Real-time Swiss Ephemeris, no cache yet |

### Gaps & Recommendations

| Gap | Priority | Fix |
|-----|----------|-----|
| No HTTP `Cache-Control` headers on stable responses | Medium | Add `Cache-Control: public, max-age=3600` to `/api/chart/public/:token`, `/api/pricing` |
| Transit data recalculated on every request | Medium | Cache transits per user in MongoDB for 1 hour |
| No CDN / edge caching | Medium | Put Cloudflare or AWS CloudFront in front; cache `/api/chart/public/*` at the edge |
| No Redis layer | Low (for now) | MongoDB caches are adequate at current scale; add Redis when p95 latency > 500 ms |
| Daily guidance collection grows unbounded | Low | Add TTL index: `db.daily_guidance.create_index("date", expireAfterSeconds=604800)` (7 days) |

---

## 2. Performance

### What's Already Implemented ✅

- Async I/O throughout (FastAPI + Motor async MongoDB driver)
- MongoDB indexes on all hot query paths (email, user_id, session_id, share_token, stripe_customer_id)
- Background tasks for email blasts (non-blocking HTTP response)
- Chat history limited to last 20 messages per session
- GZip compression middleware (responses ≥ 1 KB, added in this PR)

### Gaps & Recommendations

| Gap | Priority | Fix |
|-----|----------|-----|
| `server.py` is a 2,600-line monolith | Medium | Split into routers: `routes/auth.py`, `routes/chat.py`, etc. Improves load time and maintainability |
| No connection pool tuning for MongoDB | Medium | Set `maxPoolSize` and `minPoolSize` on `AsyncIOMotorClient`: `AsyncIOMotorClient(mongo_url, maxPoolSize=50)` |
| OpenAI calls are synchronous in fallback paths | Low | Already async; ensure no blocking `requests` calls remain |
| No streaming for AI chat responses | Low | Use `openai.chat.completions.create(stream=True)` + `StreamingResponse` for better perceived latency |
| Admin `GET /api/admin/users` loads all users (no pagination) | Medium | Add `skip`/`limit` query params (already partially done — enforce a max limit of 100) |
| `daily_guidance` collection never pruned | Low | Add MongoDB TTL index (see Caching section) |
| No uvicorn worker configuration documented | High | See Deployment section below |

---

## 3. Security

### What's Already Implemented ✅

- JWT authentication (HS256, 7-day expiry, verified on every protected route)
- bcrypt password hashing (cost factor default ~12)
- Password complexity validation (≥8 chars, letter + digit/special)
- Role-Based Access Control (admin via `ADMIN_EMAILS` env var or DB `role` field)
- Email verification (UUID token, 48-hour expiry)
- Password reset (UUID token, 1-hour expiry)
- Stripe webhook signature verification (`stripe.Webhook.construct_event`)
- CORS origins configurable via `CORS_ORIGINS` env var
- Prompt injection mitigation: user fields sanitized before being placed in LLM prompts
- Security headers on all responses: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`, `Permissions-Policy`, `Strict-Transport-Security` (added in this PR)
- Rate limiting on auth endpoints (added in this PR):
  - `POST /api/auth/register` — 10 requests/hour per IP
  - `POST /api/auth/login` — 20 requests/minute per IP
  - `POST /api/auth/forgot-password` — 5 requests/hour per IP
  - `POST /api/auth/reset-password` — 5 requests/hour per IP

### Gaps & Recommendations

| Gap | Severity | Fix |
|-----|----------|-----|
| JWT stored in `localStorage` (XSS-vulnerable) | High | Move to `HttpOnly` cookie + CSRF token. Requires frontend refactor |
| `CORS_ORIGINS` defaults to `*` in `.env.example` and code | High | Change default in `.env.example` to `http://localhost:3000` only; reject wildcard in production startup check |
| No rate limiting on AI chat endpoints | Medium | Add `@limiter.limit("60/minute")` to `POST /api/chat` and `POST /api/friend/chat` to prevent API cost abuse |
| Email blast `body_html` accepts raw HTML | Medium | Sanitize HTML server-side with `bleach` library before sending |
| No account lockout after failed logins | Medium | Track failed login attempts in DB; lock for 15 min after 10 failures |
| Password reset token is a plain UUID (guessable if DB leaked) | Low | Use `secrets.token_urlsafe(32)` instead of `str(uuid.uuid4())` |
| No audit log for admin actions | Medium | Log admin actions (tier changes, role grants, email blasts) to a dedicated `audit_log` collection |
| MongoDB connection string may contain credentials | Medium | Use MongoDB Atlas connection strings with `authMechanism=SCRAM-SHA-256`; never log `MONGO_URL` |
| `ADMIN_EMAILS` bootstraps admin without password confirmation | Low | Document this risk; admin bootstrap should only work on first login after a restart |
| No HTTPS enforcement in code | Low | Handled at reverse proxy (nginx/Caddy); add startup warning if `FRONTEND_URL` does not start with `https://` in production |

---

## 4. Server Deployment

### Recommended Stack

```
Internet → Cloudflare (CDN + DDoS) → nginx (TLS termination) → uvicorn (FastAPI)
                                                               → MongoDB Atlas
                                                               → React SPA (served from CDN)
```

### Environment Variables Checklist

Before going live, ensure **all** of the following are set correctly in your hosting platform:

```bash
# Required — app won't start without these
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/gab44?retryWrites=true&w=majority
DB_NAME=gab44
JWT_SECRET=<64-char random hex>   # python -c "import secrets; print(secrets.token_hex(32))"

# Required for auth emails
FRONTEND_URL=https://gab44.com    # NO trailing slash; used in email links

# Required for production security
CORS_ORIGINS=https://gab44.com    # Comma-separated; NEVER use * in production

# Strongly recommended
OPENAI_API_KEY=sk-proj-...
SENDGRID_API_KEY=SG....
EMAIL_NOREPLY=noreply@gab44.com
EMAIL_VERIFY=verify@gab44.com
EMAIL_SUPPORT=support@gab44.com
EMAIL_MARKETING=hello@gab44.com
STRIPE_SECRET_KEY=sk_live_...     # sk_live_ for production (not sk_test_)
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
ONESIGNAL_APP_ID=...
ONESIGNAL_API_KEY=...
ADMIN_EMAILS=nchobah@gmail.com
```

### Uvicorn Production Command

```bash
# Single-process (adequate for < 1000 concurrent users)
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1 --loop uvloop --http httptools

# Multi-process via gunicorn (for higher traffic)
gunicorn server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --timeout 120 \
  --keep-alive 5 \
  --log-level info
```

> Add `gunicorn>=21.0.0` and `uvloop>=0.19.0` and `httptools>=0.6.0` to `requirements.txt` for production.

### nginx Reverse Proxy (Recommended)

```nginx
server {
    listen 443 ssl http2;
    server_name api.gab44.com;

    ssl_certificate     /etc/letsencrypt/live/gab44.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gab44.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # Max request body size (prevent large payload attacks)
    client_max_body_size 2M;

    location / {
        proxy_pass         http://127.0.0.1:8001;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

### MongoDB Atlas Recommendations

1. Enable **IP Access List** — whitelist only your backend server IP(s)
2. Enable **Atlas Auditing** for admin DB operations
3. Set **Read/Write Concern**: `w=majority, readConcern=majority` for payment-critical operations
4. Enable **Backup** (at minimum daily snapshots)
5. Ensure **indexes** are created at startup (already done in `@app.on_event("startup")`)

### Stripe Webhook Configuration

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://api.gab44.com/api/payments/webhook`
3. Select events: `checkout.session.completed`, `customer.subscription.deleted`
4. Copy the **Signing Secret** → set as `STRIPE_WEBHOOK_SECRET`
5. The webhook handler already verifies the signature with `stripe.Webhook.construct_event` ✅

### Health Check

```bash
curl https://api.gab44.com/health
# Expected: {"status": "ok"}
```

Set this URL as the health check in Railway / Render / Fly.io / your load balancer.

---

## 5. Pre-Deployment Checklist

Run through this list before every production deploy:

- [ ] All env vars verified (see section 4)
- [ ] `CORS_ORIGINS` does NOT contain `*`
- [ ] `JWT_SECRET` is ≥ 32 random characters
- [ ] `STRIPE_SECRET_KEY` uses `sk_live_` prefix (not test key)
- [ ] Stripe webhook endpoint configured and `STRIPE_WEBHOOK_SECRET` set
- [ ] SendGrid sender addresses are verified in SendGrid dashboard
- [ ] MongoDB Atlas IP whitelist updated with new server IP
- [ ] `pytest tests/ -v` passes in CI
- [ ] `GET /health` returns `{"status": "ok"}` after deploy
- [ ] Manual smoke test: register → verify email → login → view chart → run gematria
- [ ] Admin login works and admin dashboard loads
- [ ] Stripe test checkout completes and tier upgrades correctly (use test mode first)
- [ ] Daily guidance generates and caches correctly
- [ ] Rate limit response (429) appears after 20 rapid login attempts

---

*Last updated: 2026-02-25 — covers Gab44 V2 codebase.*
