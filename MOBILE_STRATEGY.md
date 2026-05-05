# Gab44 — Phase 2 Mobile Strategy

> **Recommendation up front: Capacitor.** Wrap the existing React 19 SPA into native iOS and Android shells with Capacitor 6. Ship beta on Android in days, not months. Reserve a React-Native rewrite for v2 if (and only if) we hit a wall the web stack can't clear.

---

## Decision Matrix

| Criterion | A. Capacitor wrap | B. React Native / Expo rewrite | C. PWA only |
|---|---|---|---|
| **Time to first beta build** | 3–5 days | 6–10 weeks | 1–2 days |
| **App Store / Play Store presence** | ✅ Yes (real native binary) | ✅ Yes | ❌ No (Android allows TWA workaround; iOS doesn't) |
| **Reuses existing React 19 + Tailwind UI** | ✅ 100% as-is | ❌ Throw it away. RN has no CSS, no Tailwind out of the box, no shadcn/Radix. | ✅ 100% as-is |
| **Reuses existing 17 pages + 45 shadcn components** | ✅ All of it | ❌ Rewrite each one | ✅ All of it |
| **Push notifications** | ✅ OneSignal Capacitor plugin (we already use OneSignal) | ✅ OneSignal RN SDK | ⚠️ Web Push only (no iOS Safari yet on most installs) |
| **Native auth: Apple/Google sign-in, biometrics** | ✅ Capacitor plugins | ✅ RN packages | ⚠️ Limited |
| **In-app purchases (App Store / Play billing)** | ✅ via plugins (RevenueCat, etc.) | ✅ same | ❌ Cannot — must use external link, which Apple punishes |
| **Performance for chart rendering / chat** | ✅ Indistinguishable from web (WebView is the same engine) | ✅ Native UIView/Compose | ✅ Web speed |
| **Cost to maintain** | One codebase. One PR ships everywhere. | Two codebases (web + RN). Doubles velocity tax. | One codebase. |
| **Risk of rejection from App Store** | Low (proper native shell, real plugins) | Low | N/A |
| **Offline support** | ✅ Capacitor Storage + Service Worker | ✅ AsyncStorage / MMKV | ✅ Service Worker |
| **Total upfront engineering effort** | ~1 week | ~2–3 months | ~3 days |

**Verdict: Capacitor wins on every axis except theoretical native polish.** The codebase has a year of iteration behind it — 17 pages, 45 UI components, a designed CSS theme system, and a working AuthContext. Re-implementing this in React Native would burn a quarter and ship the same product. Capacitor lets us focus that quarter on the bot, the AI, and the chart visualization improvements that actually move retention.

---

## Why Not React Native (in detail)

1. **The design system is CSS.** `frontend/src/index.css` defines the entire Cosmic-Luxury theme as Tailwind utilities and HSL CSS variables. RN doesn't run CSS. We'd rewrite `glass-card`, `cosmic-gradient`, `glow-button`, `chat-bubble-friend` (the rose-tinted Saoul bubbles), and every shadow/blur from scratch in `StyleSheet.create()`.
2. **45 shadcn components have no RN equivalent.** Radix primitives target the DOM. We'd swap to a RN UI library (Tamagui, NativeBase, gluestack) — different API, different a11y model, different ergonomics.
3. **`react-router-dom` is web-only.** Migrate to `expo-router` or `@react-navigation/native`. Every `<Link>` and `useNavigate()` call rewritten.
4. **Recharts won't render.** Chart visualizations rebuilt with `react-native-svg` or Skia.
5. **axios-with-interceptor pattern survives**, but each page's data-fetching is rewritten because `useAuth()`, toasts, and form libraries (`react-hook-form` works, `sonner` doesn't, `react-day-picker` doesn't) all change.

The honest estimate is **6–10 weeks of one engineer, not counting QA**, and the result is a *visually different* product — not the Cosmic-Luxury web experience users will already know from `gab44.com`.

## Why Not PWA-Only

A PWA reaches Android well (Chrome supports installable PWAs, badging, web push). On **iOS** it loses: no proper App Store presence, no in-app purchases (lethal — Apple takes 30% on subscriptions and PWAs cannot use it; sending users to Stripe Checkout in Safari risks rejection of any companion native app later), and unreliable push (iOS 16.4+ supports web push only for installed PWAs and behavior is fragile). For Gab44 — a paid subscription product targeting a mainstream audience — PWA-only is **only viable if we explicitly write off the iOS App Store**. We don't.

A PWA still ships as a free side-effect (we can configure the existing site as one), but it is not the strategy.

---

## Recommended Strategy: Capacitor 6

```
                ┌─────────────────────────────────────────┐
                │   frontend/  (React 19 SPA, unchanged)  │
                │   - All 17 pages                        │
                │   - shadcn/ui components                │
                │   - Cosmic-Luxury theme                 │
                └────────────────┬────────────────────────┘
                                 │ npm run build → frontend/build/
                                 ▼
                ┌─────────────────────────────────────────┐
                │   mobile/  (Capacitor host)             │
                │   - capacitor.config.ts                 │
                │   - android/  (Gradle + Android Studio) │
                │   - ios/      (Xcode workspace)         │
                └─────────────────────────────────────────┘

                Plugins (npm install @capacitor/<x>):
                  · push-notifications  → OneSignal
                  · preferences         → token + theme persistence
                  · app + status-bar    → safe-area + dark mode
                  · share               → public chart link
                  · haptics             → coach send / friend react
                  · in-app-browser      → Stripe Checkout fallback
                  · device              → installation telemetry
                  · network             → offline detection
```

### Folder Layout (Phase 4 will scaffold this)

```
gab44/
├── backend/                 (unchanged)
├── frontend/                (unchanged — keeps building for web)
├── mobile/                  ← NEW
│   ├── capacitor.config.ts
│   ├── package.json         (depends on ../frontend/build)
│   ├── android/             (generated by `npx cap add android`)
│   └── ios/                 (generated on macOS — gitignored binaries)
├── bot/                     ← NEW (Phase 3)
└── ...
```

The web build (`frontend/build/`) is the source of truth. `capacitor.config.ts` points `webDir` at it. The mobile layer never touches the React source — it consumes the production bundle.

### Required Code Changes (small)

| File | Change |
|---|---|
| `frontend/src/App.js` | Detect Capacitor (`window.Capacitor?.isNativePlatform()`) and conditionally use `HashRouter` instead of `BrowserRouter` (file:// URLs don't support history mode cleanly without configuration). |
| `frontend/src/lib/auth-storage.js` (new) | Wrap localStorage so it falls back to `@capacitor/preferences` when running native — token survives reinstalls only if we use Keychain/Keystore. |
| `frontend/src/lib/push.js` (new) | Replace OneSignal Web SDK with `@capacitor/push-notifications` when on native. The backend endpoint `POST /notifications/register-device` is already device-agnostic — registers any player_id. |
| `frontend/src/lib/payments.js` (new) | On native iOS: warn user to subscribe via web (until we add IAP via RevenueCat in v2). On Android: open Stripe Checkout in `@capacitor/browser` then deep-link back. |
| Image/CSS | Audit `position: fixed` and `100vh` usage for safe-area insets — replace `100vh` with `100dvh` and add CSS `env(safe-area-inset-*)` padding. |
| `public/index.html` | Capacitor injects its own bridge — make sure no `<base href>` blocks it. Confirm OneSignal init doesn't run on native (let Capacitor plugin handle). |
| Backend CORS | Add `capacitor://localhost`, `ionic://localhost`, and `http://localhost` to `CORS_ORIGINS` for dev. Capacitor serves the bundle from these origins. |

That's it. The 17 pages, 45 components, every animation, every gradient ship as-is.

### App Store / Play Store

- **Android first** — quicker review, no Apple dev account needed, can side-load APK to testers in hours.
- **iOS** requires a macOS box for Xcode. We can do TestFlight builds via GitHub Actions with `xcode-build` once a paid Apple Developer account is in place.
- Bundle ID: `com.gab44.app`. App display name: `Gab44`. Use the favicon SVG as the seed asset and have the design team produce 1024×1024 + adaptive icons + splash for both platforms.
- Privacy manifest (iOS 17+): we collect email + birth date + location; declare `NSUserTrackingUsageDescription` only if we add analytics SDKs.
- Permissions: push notifications (opt-in), no camera/mic/contacts.

### Auth Flow on Mobile

The existing JWT-in-localStorage flow ports as-is. With `@capacitor/preferences` we get OS-level encrypted storage on both platforms. **Recommendation:** add a "Sign in with Apple / Google" path post-launch — they're table stakes for 2026 mobile apps and Apple actually requires Sign-in-with-Apple if any other social sign-in is offered.

### Deep Linking

- Web: `https://gab44.com/chart/public/<token>`
- iOS Universal Links + Android App Links: same URLs route into the app when installed. Configured via `apple-app-site-association` and `assetlinks.json` served from the marketing site at `/.well-known/`.

### Offline Strategy (v1)

- Cache the last-fetched birth chart and daily guidance in `@capacitor/preferences`.
- Show a stale-but-readable view if the network is down.
- Coach / Friend / new transit calculations stay online-only — they're LLM and ephemeris calls that need the server.

### Performance Notes

- Capacitor on iOS uses WKWebView (Safari engine); on Android, Chromium WebView. Both run our React 19 bundle without modification.
- The single-bundle webpack output is currently un-split — a `craco` config tweak to enable route-level code splitting is the highest-leverage perf fix before mobile launch (cuts cold-start TTI dramatically on mid-tier Android).

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Apple rejects an app that links out for billing | Ship Android first; add RevenueCat IAP for iOS before submitting to App Store. |
| WebView performance on cheap Android devices | Enable code-splitting; preload chart data on boot; lazy-load heavy pages (Compatibility, Numerology, Gematria). |
| Safe-area / notch issues on iPhone 14+ | One pass through the design system to add `env(safe-area-inset-top)` to the glass header. |
| Push notification setup is delicate | Use OneSignal's Capacitor plugin (mature) — same backend code as today. |
| Stripe webhook bypass bug (REVIEW §3.1) | Fix in Phase 4 before mobile sees production traffic. |

---

## What Phase 4 Will Build (mobile slice)

1. `mobile/` directory with `capacitor.config.ts`.
2. `npx cap add android` (generates `mobile/android/` Gradle project).
3. Build script: `cd frontend && npm run build && cd ../mobile && npx cap sync android`.
4. Patch `frontend/src/App.js` for `HashRouter` on native.
5. Add platform-aware `auth-storage`, `push`, and `payments` shims.
6. Add `capacitor://localhost` to backend `CORS_ORIGINS`.
7. Verify the APK boots, logs in against the Hetzner backend, fetches a chart.
8. Document the build → emulator → device pipeline in `mobile/README.md`.

iOS scaffold is **not** in Phase 4 — it requires macOS. We'll add it in a follow-up pass on a Mac runner.

---

## Long-Term: when (if) to revisit React Native

Switch to RN only if we hit one of these:
- Animations or chart rendering need 60fps that WebView can't deliver — unlikely for chat-and-cards UX.
- Apple starts cracking down on web-content apps (no signal of this in 2026).
- We add a feature that genuinely requires native UIKit / Compose (live activities, widgets, watch app).

Until then, every hour saved on the mobile shell is an hour invested in the AI coach, the bot, and the things users actually pay for.
