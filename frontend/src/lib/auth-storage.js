// Small wrapper around credential storage. On the web we use localStorage so
// the existing behaviour is unchanged. On native (Capacitor) we'd prefer the
// OS-encrypted Preferences API; until @capacitor/preferences is installed in
// the mobile shell we fall back to localStorage there too — works fine in the
// WebView, just less secure than Keychain/Keystore.

import { isNative } from "./platform";

const KEY = "gab44_token";

let nativePreferences = null;

if (isNative()) {
  // Lazy import so the web build never bundles the native plugin.
  // The mobile/ Capacitor project lists @capacitor/preferences as a dep.
  // eslint-disable-next-line @typescript-eslint/no-var-requires, no-undef
  import("@capacitor/preferences")
    .then((mod) => {
      nativePreferences = mod.Preferences;
    })
    .catch(() => {
      // Plugin not installed (e.g. running web build inside a custom WebView):
      // silently fall back to localStorage.
    });
}

export const getToken = async () => {
  if (nativePreferences) {
    const { value } = await nativePreferences.get({ key: KEY });
    return value || null;
  }
  return localStorage.getItem(KEY);
};

export const setToken = async (token) => {
  if (nativePreferences) {
    await nativePreferences.set({ key: KEY, value: token });
    return;
  }
  localStorage.setItem(KEY, token);
};

export const clearToken = async () => {
  if (nativePreferences) {
    await nativePreferences.remove({ key: KEY });
    return;
  }
  localStorage.removeItem(KEY);
};

// Synchronous escape hatch for the existing AuthProvider boot path, which
// reads the token before any await. On web this is just localStorage; on
// native it's a best-effort cached lookup that may be empty on first boot
// (the async getToken() call right after will fix it).
export const getTokenSync = () => {
  return localStorage.getItem(KEY);
};
