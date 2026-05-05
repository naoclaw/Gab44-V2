# Gab44 Mobile (Capacitor)

This folder wraps the existing React 19 SPA from `../frontend/` into native iOS and Android shells with **Capacitor 6**.  
For the rationale behind this choice see `../MOBILE_STRATEGY.md`.

---

## One-time setup

You need this on the dev machine:

| Tool | Why |
|---|---|
| Node 18+ | Capacitor CLI |
| JDK 17 + Android Studio (Hedgehog or newer) | Android build |
| Xcode 15 + CocoaPods (macOS only) | iOS build |

Then:

```bash
cd mobile
npm install
```

This installs the Capacitor CLI and core plugins. **The native folders (`android/`, `ios/`) are NOT committed** — they're generated locally so the repo stays clean.

---

## Quick start (Android)

```bash
# 1. Build the React app — outputs to ../frontend/build/
npm run build:web

# 2. Add the Android shell (only first time)
npm run android:add

# 3. Sync the web build into the native project
npm run sync

# 4. Open Android Studio (Run ▶ on a device or emulator)
npm run android:open

# Or skip the IDE and run on the first attached device:
npm run android:run
```

End-to-end shortcut: `npm run build:android`.

---

## Quick start (iOS, macOS only)

```bash
npm run build:web
npm run ios:add        # first time
npm run sync
npm run ios:open
```

---

## What lives where

| Path | What it is |
|---|---|
| `capacitor.config.ts` | App ID (`com.gab44.app`), name, webDir → `../frontend/build`, plugin config. |
| `package.json` | Capacitor + plugin deps and convenience scripts. |
| `android/`, `ios/` | Generated native projects (gitignored). Treat as build output unless you need native customizations — then commit them deliberately. |

---

## Code that already supports the mobile target

The frontend has been patched to be Capacitor-aware (kept tiny):

- `frontend/src/lib/platform.js` — `isNative()` detects whether we're inside the WebView.
- `frontend/src/lib/auth-storage.js` — wraps `localStorage` so on native it falls through to `@capacitor/preferences` (OS-level encrypted storage).
- `frontend/src/App.js` — switches to `HashRouter` when `isNative()` so file:// URLs route correctly.

Adding more native capability (push, share, haptics) means writing thin wrappers that no-op on web and call the Capacitor plugin on native — see `lib/auth-storage.js` for the pattern.

---

## Backend CORS

The bundle is served from a custom scheme on each platform:

- iOS: `capacitor://localhost`
- Android: `https://localhost` (with `androidScheme: 'https'`)

Make sure these are in `CORS_ORIGINS` on the backend before testing logged-in flows. Example:

```env
CORS_ORIGINS=https://gab44.com,capacitor://localhost,https://localhost
```

---

## Push notifications

We already use **OneSignal** on the web. For native we'll route through OneSignal's Capacitor plugin (added in v1.1) and post the `playerId` to the existing `POST /api/notifications/register-device`. The backend endpoint is device-agnostic, no changes needed.

---

## Builds & releases (next milestones)

- **Internal testing build:** `cap build android` produces an unsigned APK; share via Diawi or Firebase App Distribution.
- **Play Store:** generate a signed AAB, configure Internal Testing track in Google Play Console.
- **iOS TestFlight:** requires a paid Apple Developer account and macOS runner.

CI will live in `.github/workflows/mobile.yml` once we agree on signing material storage (likely GitHub Secrets + match for iOS).

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `cap sync` says "no platform added" | Run `npm run android:add` first. |
| White screen on launch | The web build wasn't synced — re-run `npm run build:web && npm run sync`. |
| 401 / login loop on device | Backend CORS is rejecting the Capacitor scheme — add `capacitor://localhost` and `https://localhost` to `CORS_ORIGINS`. |
| Camera/biometrics needed | Add the relevant `@capacitor/<plugin>` and update `ios/App/App/Info.plist` permission strings. |
