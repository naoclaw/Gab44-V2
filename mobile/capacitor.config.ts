import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.gab44.app',
  appName: 'Gab44',
  // Points at the React build that lives in the sibling frontend/ folder.
  // Run `npm run build:web` in this directory before `cap sync`.
  webDir: '../frontend/build',

  bundledWebRuntime: false,

  // Native platforms render the SPA from a custom scheme; keep it explicit so
  // backend CORS configuration lines up.
  server: {
    androidScheme: 'https',
    iosScheme: 'https',
    // Uncomment during dev to live-reload from the React dev server on the
    // host machine (replace with your LAN IP).
    // url: 'http://192.168.1.42:3000',
    // cleartext: true,
  },

  android: {
    allowMixedContent: false,
    backgroundColor: '#0c0c14', // Cosmic-Luxury dark background
  },

  ios: {
    contentInset: 'always',
    backgroundColor: '#0c0c14',
  },

  plugins: {
    SplashScreen: {
      launchShowDuration: 1200,
      launchAutoHide: true,
      backgroundColor: '#0c0c14',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#0c0c14',
    },
  },
};

export default config;
