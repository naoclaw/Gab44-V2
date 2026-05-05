import { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/context/ThemeContext";
import { ReadingModeProvider } from "@/context/ReadingModeContext";

// Pages
import LandingPage from "@/pages/LandingPage";
import AuthPage from "@/pages/AuthPage";
import Dashboard from "@/pages/Dashboard";
import ChatPage from "@/pages/ChatPage";
import FriendPage from "@/pages/FriendPage";
import ChartPage from "@/pages/ChartPage";
import TransitsPage from "@/pages/TransitsPage";
import PricingPage from "@/pages/PricingPage";
import SettingsPage from "@/pages/SettingsPage";
import ShareChartPage from "@/pages/ShareChartPage";
import AdminPage from "@/pages/AdminPage";
import CompatibilityPage from "@/pages/CompatibilityPage";
import VerifyEmailPage from "@/pages/VerifyEmailPage";
import ResetPasswordPage from "@/pages/ResetPasswordPage";
import PublicChartPage from "@/pages/PublicChartPage";
import NumerologyPage from "@/pages/NumerologyPage";
import GematriaPage from "@/pages/GematriaPage";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("gab44_token"));
  const [loading, setLoading] = useState(true);

  const logout = () => {
    localStorage.removeItem("gab44_token");
    setToken(null);
    setUser(null);
  };

  // Global Axios interceptor: auto-logout when any API call returns 401
  // (e.g. JWT expired mid-session). Runs once on mount.
  useEffect(() => {
    const interceptorId = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          const currentToken = localStorage.getItem("gab44_token");
          // Only trigger if the user was actually logged in (avoid loop on the
          // /auth/login or /auth/me calls that fire before session is set)
          if (currentToken) {
            localStorage.removeItem("gab44_token");
            setToken(null);
            setUser(null);
            import("sonner").then(({ toast }) => {
              toast.error("Your session has expired. Please sign in again.");
            });
            // Redirect to auth after a brief delay so the toast is visible first
            setTimeout(() => {
              if (!window.location.pathname.startsWith("/auth")) {
                window.location.href = "/auth";
              }
            }, 1500);
          }
        }
        return Promise.reject(error);
      }
    );
    return () => axios.interceptors.response.eject(interceptorId);
  }, []);

  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUser(response.data);
        } catch (error) {
          console.error("Token verification failed:", error);
          localStorage.removeItem("gab44_token");
          setToken(null);
        }
      }
      setLoading(false);
    };
    verifyToken();
  }, [token]);

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    const { access_token, user: userData } = response.data;
    localStorage.setItem("gab44_token", access_token);
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const register = async (userData) => {
    const response = await axios.post(`${API}/auth/register`, userData);
    const { access_token, user: newUser } = response.data;
    localStorage.setItem("gab44_token", access_token);
    setToken(access_token);
    setUser(newUser);
    return newUser;
  };

  const updateUser = (updatedData) => {
    setUser(prev => ({ ...prev, ...updatedData }));
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, updateUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-primary/40" />
        </div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/auth" replace />;
  }
  
  return children;
};

// Admin Route Component
const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-primary/40" />
        </div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/auth" replace />;
  }
  
  if (!user.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};


// 404 Not Found Page Component
const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold text-primary mb-4">404</h1>
        <h2 className="text-2xl font-semibold mb-4">Page Not Found</h2>
        <p className="text-muted-foreground mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <a 
          href="/dashboard"
          className="inline-flex items-center justify-center px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity"
        >
          Go to Dashboard
        </a>
      </div>
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
    <ReadingModeProvider>
      <AuthProvider>
        <div className="App min-h-screen bg-background theme-transition">
          <div className="noise-overlay" />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />
              <Route path="/chart/public/:token" element={<PublicChartPage />} />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/chat" 
                element={
                  <ProtectedRoute>
                    <ChatPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/friend" 
                element={
                  <ProtectedRoute>
                    <FriendPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/chart" 
                element={
                  <ProtectedRoute>
                    <ChartPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/transits" 
                element={
                  <ProtectedRoute>
                    <TransitsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/settings" 
                element={
                  <ProtectedRoute>
                    <SettingsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/share" 
                element={
                  <ProtectedRoute>
                    <ShareChartPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/compatibility" 
                element={
                  <ProtectedRoute>
                    <CompatibilityPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/numerology" 
                element={
                  <ProtectedRoute>
                    <NumerologyPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/gematria" 
                element={
                  <ProtectedRoute>
                    <GematriaPage />
                  </ProtectedRoute>
                } 
              />
              <Route
                path="/admin"
                element={
                  <AdminRoute>
                    <AdminPage />
                  </AdminRoute>
                }
              />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BrowserRouter>
          <Toaster position="top-right" />
        </div>
      </AuthProvider>
    </ReadingModeProvider>
    </ThemeProvider>
  );
}

export default App;
