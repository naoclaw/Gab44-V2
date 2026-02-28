# Gab44 — Failed Request Systems: Audit & Execution Plan

> Prepared 2026-02-28. No code was changed to produce this document.
> Every finding is backed by the file + line numbers listed.

---

## 1. Methodology

The audit covered every request path in the system:

| Layer | Files inspected |
|-------|----------------|
| **Backend HTTP API** | `backend/server.py` (2822 lines) |
| **Frontend pages** | All 17 `frontend/src/pages/*.jsx` files |
| **Frontend shared helpers** | `frontend/src/lib/utils.js`, `frontend/src/App.js` |
| **Email (SendGrid)** | `send_email()` helper + every call site |
| **Payments (Stripe)** | Checkout, portal, and webhook endpoints |
| **Push (OneSignal)** | `send_onesignal_notification()` helper + caller |
| **AI calls (OpenAI)** | All three AI helper functions |

---

## 2. Current State — What Is Already Working Well

These patterns already exist and should **not** be changed:

- **Global Axios 401 interceptor** (`App.js:56-76`) — auto-logout + toast when JWT expires mid-session.
- **`parseApiError()` utility** (`lib/utils.js`) — correctly normalises Pydantic 422 arrays and plain strings.
- **`send_email()` never throws** — returns `False` and logs on failure; callers never crash if SendGrid is down.
- **OpenAI helper fallbacks** — `get_ai_coach_response`, `get_ai_friend_response`, `generate_compatibility_analysis` all catch exceptions and return a graceful English fallback string, so the HTTP endpoint still returns 200.
- **Daily guidance LLM fallback** — if GPT-4o fails, a static guidance block is returned and cached (`server.py:1992`).
- **Stripe webhook signature verification** — catches `ValueError` and `SignatureVerificationError`, returns 400 (`server.py:2393`).
- **OneSignal helper** — catches all exceptions, logs, and returns `False`.
- **Rate-limit handler** — `RateLimitExceeded` is wired to `_rate_limit_exceeded_handler` which returns a clean 429.
- **Newsletter subscribe** — treats `catch {}` as success on both error/success to avoid disclosing existence of email (`LandingPage.jsx:621`).

---

## 3. Issues Found — Grouped by Severity

### 🔴 CRITICAL — Request can crash the server (unhandled exception → 500)

| # | Location | Problem |
|---|----------|---------|
| C1 | `server.py:1400–1445` (`GET /chart/me`) | `calculate_natal_chart()` is called **outside any try/except**. A Swiss Ephemeris error or malformed date throws an unhandled exception and returns a raw 500, not a clean 500 with a user-facing detail message. Same for `calculate_numerology()` and `calculate_gematria()` on the same code path. |
| C2 | `server.py:2046–2053` (`POST /compatibility/analyze`) | Both `calculate_natal_chart()` calls (user chart + partner chart) are outside any try/except. Any bad birth date/place raises an unhandled 500. |
| C3 | `server.py:2320–2360` (`POST /payments/create-checkout-session`) | `stripe.Customer.create()` and `stripe.checkout.Session.create()` are called outside any try/except (only the surrounding `if not STRIPE_SECRET_KEY` guard exists). A Stripe network error or card-declined response propagates as an unhandled 500. |
| C4 | `server.py:2363–2373` (`POST /payments/portal`) | `stripe.billing_portal.Session.create()` is outside any try/except. A Stripe API error returns a raw 500. |

---

### 🟠 HIGH — Silent failure — request "succeeds" but user gets no feedback

| # | Location | Problem |
|---|----------|---------|
| H1 | `frontend/src/pages/ChartPage.jsx:105-106` | `catch(error)` only calls `console.error`. The page renders normally but `chart` state stays `null`. The UI shows nothing; the user sees a blank page with no error state or retry button. |
| H2 | `frontend/src/pages/TransitsPage.jsx:42-43` | Same pattern. `transits` stays `[]`. The page renders an empty list with no message to the user about whether it errored or is just empty. |
| H3 | `frontend/src/pages/NumerologyPage.jsx:107-108` | `profile` stays `null`. Page renders its loading skeleton forever or shows a blank section. |
| H4 | `frontend/src/pages/GematriaPage.jsx:116-117` | `result` stays its previous value (or `null`). User gets no indication the calculation failed. |
| H5 | `frontend/src/pages/CompatibilityPage.jsx:190-191` | `fetchReports()` fails silently. The reports list stays empty with no error message. |
| H6 | `frontend/src/pages/Dashboard.jsx:240-241` | The outer `catch` for `guidanceRes` (the critical daily guidance call) only does `console.error`. If guidance fails, `dailyGuidance` stays `null`. The dashboard renders empty cards with no error state. Transits/numerology do have `.catch()` fallbacks (lines 232/235), but the primary guidance does not. |
| H7 | `frontend/src/pages/ShareChartPage.jsx:168-169` | Chart fetch for the share page fails silently; `chart` stays `null`, but the page renders with no error state. |
| H8 | `frontend/src/pages/AdminPage.jsx:74-76` | Admin data fetch shows a toast but sets no error state. When retrying, `users` stays `[]` and the table renders empty with no retry button. |

---

### 🟡 MEDIUM — Incomplete error information

| # | Location | Problem |
|---|----------|---------|
| M1 | `server.py:2476–2514` (`POST /subscribe`) | Newsletter subscription endpoint has no try/except around the `db.newsletter_subscribers.insert_one()` call. A MongoDB write failure returns a raw 500 instead of a friendly message. (The email send is protected, but the DB write is not.) |
| M2 | `server.py:2513–2562` (`POST /contact`) | The contact form endpoint has no try/except around the DB write or around `send_email` to support inbox. If the DB fails, 500. If the support email fails, it's silent (no notification to admins that a ticket was lost). |
| M3 | `server.py:2647–2665` (`PUT /admin/users/{user_id}/tier`) — `tier` is accepted **as a query parameter**, not a request body field. Same for `PUT /admin/users/{user_id}/role` (`server.py:2664–2682`). This is non-RESTful and is tracked separately in issue #52, but failing inputs produce unhelpful 422s rather than a clear error. |
| M4 | `frontend/src/pages/PricingPage.jsx:26-27` | Pricing fetch fails silently (`console.error`). If the backend pricing endpoint is down, the page renders empty cards with no message. |
| M5 | `frontend/src/pages/Dashboard.jsx:230-236` | When the outer `guidanceRes` request throws (e.g. network error), the other two `.catch()` fallbacks never run because `Promise.all` rejects immediately. Only the `console.error` runs. No user-visible feedback. |
| M6 | `server.py:1469–1495` (`GET /numerology/profile`) | `numerology_full_profile()` (external module call) is not wrapped in try/except. A failure in the numerology engine crashes the request with 500. |
| M7 | `server.py:1497–1508` (`POST /gematria/calculate`) | `gematria_calculate_all()` is not wrapped in try/except. A failure in the gematria engine crashes the request with 500. |

---

### 🔵 LOW — Polish / UX improvement

| # | Location | Problem |
|---|----------|---------|
| L1 | **No React Error Boundary** in `index.js` or `App.js`. An uncaught JavaScript exception in any page component crashes the entire SPA (blank white screen, no message). |
| L2 | `server.py` — No global FastAPI exception handler for unhandled exceptions. Currently a 500 returns FastAPI's default `{"detail": "Internal Server Error"}` with no request ID, making logs difficult to correlate. |
| L3 | `frontend/src/pages/AdminPage.jsx` — `updateUserTier` and `toggleAdminRole` catch blocks show `toast.error("Failed to update user")` with no retry mechanism. The UI table row stays in a stale state. |
| L4 | `frontend/src/App.js:67-70` — 401 interceptor shows a toast and clears state, but does **not** redirect the user to `/auth`. The user sees the toast but remains on a protected page that re-fires requests (creating an error loop) until they navigate manually. |
| L5 | `frontend/src/pages/ChatPage.jsx` / `FriendPage.jsx` — When `fetchSessions` fails (lines 56-57 / 57-58), the sessions list is silently empty. The user can't see past conversations but gets no explanation. |
| L6 | `server.py:2392-2396` (Stripe webhook) — When webhook signature verification fails and a legitimate event is dropped, there is no alert or metric. Stripe will retry (exponential backoff), but repeated silent drops are undetectable. |
| L7 | Email blast (`server.py:_do_email_blast`) runs as a `BackgroundTasks` worker with no error collection. If 50% of emails fail, the admin gets no report — only server logs. |

---

## 4. Execution Plan (Priority Order)

### Phase 1 — Fix server crashes (CRITICAL) [~2 hrs]

**File: `backend/server.py`**

1. **C1** — Wrap the chart calculation block in `GET /chart/me` in try/except:
   ```python
   try:
       chart_data = calculate_natal_chart(...)
       numerology = ...
       gematria = ...
   except Exception as e:
       logging.error("Chart calculation failed for user %s: %s", user["id"], e)
       raise HTTPException(status_code=500, detail="Chart calculation failed. Please try again.")
   ```

2. **C2** — Same pattern for both `calculate_natal_chart` calls in `POST /compatibility/analyze`.

3. **C3** — Wrap `stripe.Customer.create()` and `stripe.checkout.Session.create()` in `POST /payments/create-checkout-session`:
   ```python
   except stripe.error.StripeError as e:
       logging.error("Stripe checkout error for user %s: %s", user["id"], e)
       raise HTTPException(status_code=502, detail="Payment service unavailable. Please try again.")
   ```

4. **C4** — Same pattern for `POST /payments/portal`.

**Tests to add:**
- `tests/test_error_handling.py` — mock `calculate_natal_chart` to raise, assert 500 with detail.
- Mock `stripe.checkout.Session.create` to raise `stripe.error.APIConnectionError`, assert 502.

---

### Phase 2 — Add frontend error states (HIGH) [~3 hrs]

**Approach:** Each page that has a silent catch needs three things:
1. An `error` state variable (`useState(null)`)
2. The catch block sets it: `setError("Could not load your chart. Please try again.")`
3. A conditional render above the main content:
   ```jsx
   {error && (
     <div className="text-center py-12">
       <p className="text-muted-foreground mb-4">{error}</p>
       <Button onClick={retry}>Try again</Button>
     </div>
   )}
   ```

**Pages to update (in order):**

| Page | State var | Retry action |
|------|-----------|-------------|
| `ChartPage.jsx` | `chartError` | re-call `fetchChart()` |
| `TransitsPage.jsx` | `transitsError` | re-call fetch |
| `NumerologyPage.jsx` | `profileError` | re-call `fetchProfile()` |
| `GematriaPage.jsx` | `calcError` | show inline below input |
| `CompatibilityPage.jsx` | `reportsError` | re-call `fetchReports()` |
| `ShareChartPage.jsx` | `chartError` | re-call fetch |
| `PricingPage.jsx` | `pricingError` | re-call fetch |

**Dashboard special case (H6 + M5):** Switch from `Promise.all` to `Promise.allSettled` so a guidance failure doesn't kill transits/numerology, and show a per-card error state.

---

### Phase 3 — Fix silent server failures (MEDIUM) [~1.5 hrs]

**File: `backend/server.py`**

5. **M1** — Wrap the `db.newsletter_subscribers.insert_one()` call in try/except:
   ```python
   except Exception as e:
       logging.error("Newsletter subscribe DB error: %s", e)
       raise HTTPException(status_code=500, detail="Subscription failed. Please try again.")
   ```

6. **M2** — Wrap `db.contact_messages.insert_one()` in `POST /contact` in try/except. Also log when the support forward email fails (it currently silently drops).

7. **M6** — Wrap `numerology_full_profile()` in `GET /numerology/profile`:
   ```python
   try:
       profile = numerology_full_profile(full_name, birth_date)
   except Exception as e:
       logging.error("Numerology profile error: %s", e)
       raise HTTPException(status_code=500, detail="Numerology calculation failed.")
   ```

8. **M7** — Same pattern for `gematria_calculate_all()` in `POST /gematria/calculate`.

---

### Phase 4 — UX Polish (LOW) [~2 hrs]

9. **L1** — Add a React Error Boundary component to `index.js`:
   ```jsx
   // frontend/src/components/ErrorBoundary.jsx
   class ErrorBoundary extends React.Component {
     state = { hasError: false };
     static getDerivedStateFromError() { return { hasError: true }; }
     componentDidCatch(error, info) { console.error("Uncaught:", error, info); }
     render() {
       if (this.state.hasError) return <ErrorPage />;
       return this.props.children;
     }
   }
   ```
   Wrap `<App />` in `index.js`.

10. **L2** — Add a global FastAPI exception handler that logs and returns a request ID:
    ```python
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = str(uuid.uuid4())[:8]
        logging.error("Unhandled exception [%s] %s %s: %s", request_id, request.method, request.url.path, exc)
        return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred.", "request_id": request_id})
    ```

11. **L4** — In the 401 interceptor (`App.js`), add `window.location.href = "/auth"` after clearing state:
    ```js
    setToken(null);
    setUser(null);
    // redirect after brief delay to allow toast to show
    setTimeout(() => { window.location.href = "/auth"; }, 1500);
    ```

12. **L5** — `ChatPage.jsx` / `FriendPage.jsx`: show a toast when `fetchSessions` fails.

13. **L6** — For the email blast background worker, collect errors and return a summary: `{"queued": N, "failed": M}`.

---

## 5. Request Surfaces Summary Table

| Surface | Request type | Auth | Error on failure | User feedback |
|---------|-------------|------|-----------------|---------------|
| `POST /auth/register` | MongoDB write + email | None | 400 if dupe | ✅ `parseApiError` |
| `POST /auth/login` | MongoDB read + JWT | None | 401 | ✅ `parseApiError` |
| `GET /auth/me` | MongoDB read | JWT | 401 | ✅ auto-logout |
| `PUT /auth/me` | MongoDB write | JWT | 400/404 | ✅ per-field |
| `POST /auth/forgot-password` | MongoDB write + email | None | Always 200 | ✅ anti-enumeration |
| `POST /auth/reset-password` | MongoDB write | None | 400 | ✅ `parseApiError` |
| `GET /chart/me` | SwissEph + MongoDB | JWT | **🔴 unhandled 500** | ❌ blank page |
| `GET /transits/upcoming` | SwissEph | JWT | 422 if no birth_date | ❌ silent empty list |
| `GET /guidance/daily` | MongoDB + OpenAI | JWT | ✅ has fallback | ❌ no error state in UI |
| `POST /chat` | OpenAI + MongoDB | JWT | 429 or ✅ fallback | ✅ toast |
| `POST /friend/chat` | OpenAI + MongoDB | JWT | 429 or ✅ fallback | ✅ toast |
| `GET /numerology/me` | MongoDB read | JWT | Returns `{}` on fail | ❌ silent |
| `GET /numerology/profile` | numerology engine | JWT | **🔴 unhandled 500** | ❌ blank page |
| `POST /gematria/calculate` | gematria engine | None | **🔴 unhandled 500** | ❌ silent |
| `POST /compatibility/analyze` | SwissEph + OpenAI | JWT | **🔴 unhandled 500** | ❌ generic toast |
| `POST /payments/create-checkout-session` | Stripe | JWT | **🔴 unhandled 500** | ❌ partially handled |
| `POST /payments/portal` | Stripe | JWT | **🔴 unhandled 500** | ✅ toast (catches HTTP, not Stripe errors) |
| `POST /payments/webhook` | Stripe | Sig verify | ✅ 400 on bad sig | N/A (server-to-server) |
| `POST /subscribe` | MongoDB write + email | None | **🟠 unhandled 500 on DB error** | ✅ silent success on failure |
| `POST /contact` | MongoDB write + 2x email | None | **🟠 unhandled 500 on DB error** | ✅ toast |
| `POST /notifications/register-device` | MongoDB write | JWT | 400 | ✅ toast |
| `POST /admin/*` | MongoDB | JWT+Admin | 400/404 | ✅ toast (mostly) |

---

## 6. Files to Change (Next Session)

```
backend/server.py                              # C1–C4, M1–M2, M6–M7, L2
frontend/src/pages/ChartPage.jsx               # H1
frontend/src/pages/TransitsPage.jsx            # H2
frontend/src/pages/NumerologyPage.jsx          # H3
frontend/src/pages/GematriaPage.jsx            # H4
frontend/src/pages/CompatibilityPage.jsx       # H5
frontend/src/pages/Dashboard.jsx              # H6, M5
frontend/src/pages/ShareChartPage.jsx          # H7
frontend/src/pages/PricingPage.jsx             # M4
frontend/src/App.js                            # L4
frontend/src/components/ErrorBoundary.jsx      # L1 (new file)
frontend/src/index.js                          # L1
```

---

*Next step: implement Phase 1 (CRITICAL backend crashes) in the next session, then proceed through phases.*
