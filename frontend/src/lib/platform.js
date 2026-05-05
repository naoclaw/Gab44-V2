// Detects whether the SPA is running inside a Capacitor WebView (iOS / Android)
// vs a browser. Capacitor injects window.Capacitor at runtime when native; on
// web it's undefined.

export const isNative = () => {
  if (typeof window === "undefined") return false;
  return Boolean(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());
};

export const platform = () => {
  if (!isNative()) return "web";
  return window.Capacitor?.getPlatform?.() || "web";
};
