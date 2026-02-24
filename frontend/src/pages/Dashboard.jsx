import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTheme } from "@/context/ThemeContext";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { 
  Sparkles, 
  MessageCircle, 
  BarChart3, 
  Calendar, 
  LogOut,
  ChevronRight,
  Sun,
  Moon,
  Star,
  Zap,
  TrendingUp,
  Target,
  Settings,
  Share2,
  Menu,
  X,
  Shield,
  Heart,
  Hash,
  Coffee
} from "lucide-react";

const Sidebar = ({ activeTab, setActiveTab, mobileOpen, setMobileOpen }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const baseNavItems = [
    { id: "overview", icon: BarChart3, label: "Overview" },
    { id: "chat", icon: MessageCircle, label: "AI Coach", href: "/chat" },
    { id: "friend", icon: Coffee, label: "AI Friend", href: "/friend" },
    { id: "chart", icon: Sun, label: "Birth Chart", href: "/chart" },
    { id: "compatibility", icon: Heart, label: "Compatibility", href: "/compatibility" },
    { id: "transits", icon: Calendar, label: "Transits", href: "/transits" },
    { id: "share", icon: Share2, label: "Share Chart", href: "/share" },
    { id: "settings", icon: Settings, label: "Settings", href: "/settings" },
  ];
  
  // Only show admin link if user is admin
  const navItems = user?.is_admin 
    ? [...baseNavItems, { id: "admin", icon: Shield, label: "Admin", href: "/admin" }]
    : baseNavItems;

  const handleNavClick = (item) => {
    if (item.href) {
      navigate(item.href);
    } else {
      setActiveTab(item.id);
    }
    setMobileOpen(false);
  };

  const sidebarContent = (
    <>
      <div className="p-6 border-b border-border">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <span className="font-serif text-xl text-foreground">Gab44</span>
        </Link>
      </div>

      <nav className="flex-1 p-4 overflow-y-auto">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => handleNavClick(item)}
                className={`sidebar-link w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all ${
                  activeTab === item.id 
                    ? 'active' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
                data-testid={`nav-${item.id}`}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t border-border space-y-4">
        <button
          onClick={toggleTheme}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-all"
          data-testid="sidebar-theme-toggle"
        >
          {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          {theme === "dark" ? "Light Mode" : "Dark Mode"}
        </button>

        <div className="glass-card rounded-xl p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center font-serif text-primary">
              {user?.name?.[0] || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-foreground truncate">{user?.name}</p>
              <p className="text-xs text-muted-foreground">{user?.sun_sign || "Seeker"}</p>
            </div>
          </div>
          <div className="zodiac-badge rounded-full px-3 py-1 text-xs inline-flex items-center gap-1">
            <Star className="w-3 h-3" />
            {user?.subscription_tier || "Seeker"} Plan
          </div>
        </div>

        <Button 
          variant="ghost" 
          className="w-full justify-start text-muted-foreground hover:text-foreground"
          onClick={logout}
          data-testid="logout-btn"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Sign Out
        </Button>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 bg-card/50 backdrop-blur-sm border-r border-border flex-col h-screen fixed left-0 top-0 z-40">
        {sidebarContent}
      </aside>

      {/* Mobile Overlay */}
      {mobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <aside className={`lg:hidden fixed top-0 left-0 h-screen w-72 bg-card border-r border-border flex flex-col z-50 transform transition-transform duration-300 ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <button 
          onClick={() => setMobileOpen(false)}
          className="absolute top-4 right-4 w-8 h-8 rounded-lg bg-muted flex items-center justify-center"
        >
          <X className="w-5 h-5" />
        </button>
        {sidebarContent}
      </aside>
    </>
  );
};

const MobileHeader = ({ setMobileOpen }) => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <header className="lg:hidden fixed top-0 left-0 right-0 z-30 glass-header p-4">
      <div className="flex items-center justify-between">
        <button 
          onClick={() => setMobileOpen(true)}
          className="w-10 h-10 rounded-xl bg-muted/50 flex items-center justify-center"
          data-testid="mobile-menu-btn"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <Link to="/" className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          <span className="font-serif text-lg text-foreground">Gab44</span>
        </Link>

        <button
          onClick={toggleTheme}
          className="w-10 h-10 rounded-xl bg-muted/50 flex items-center justify-center"
        >
          {theme === "dark" ? <Sun className="w-5 h-5 text-primary" /> : <Moon className="w-5 h-5" />}
        </button>
      </div>
    </header>
  );
};

const DashboardOverview = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [dailyGuidance, setDailyGuidance] = useState(null);
  const [transits, setTransits] = useState([]);
  const [numerology, setNumerology] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [guidanceRes, transitsRes, numerologyRes] = await Promise.all([
          axios.get(`${API}/guidance/daily`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/transits/upcoming`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/numerology/me`, {
            headers: { Authorization: `Bearer ${token}` }
          }).catch((err) => { console.warn("Numerology fetch failed:", err); return { data: null }; })
        ]);
        setDailyGuidance(guidanceRes.data);
        setTransits(transitsRes.data.slice(0, 3));
        setNumerology(numerologyRes.data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="glass-card rounded-xl p-6 h-48 skeleton" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6 lg:space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="font-serif text-2xl lg:text-3xl text-foreground mb-2">
          Welcome back, {user?.name?.split(" ")[0]}
        </h1>
        <p className="text-muted-foreground text-sm lg:text-base">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Daily Energy - Large */}
        <div className="glass-card rounded-xl p-5 lg:p-6 md:col-span-2 lg:row-span-2" data-testid="daily-energy-card">
          <div className="flex items-center gap-2 mb-4">
            <Sun className="w-5 h-5 text-primary" />
            <h2 className="font-medium text-foreground">Daily Energy</h2>
          </div>
          <p className="text-muted-foreground mb-6 leading-relaxed text-sm lg:text-base">
            {dailyGuidance?.overall_energy || "Loading your cosmic guidance..."}
          </p>
          
          <div className="space-y-3 lg:space-y-4">
            <h3 className="text-sm font-medium text-foreground">Focus Areas Today</h3>
            {dailyGuidance?.focus_areas?.map((area, i) => (
              <div key={i} className="flex items-center gap-3 text-sm text-muted-foreground">
                <Target className="w-4 h-4 text-primary flex-shrink-0" />
                {area}
              </div>
            ))}
          </div>

          <Button 
            className="mt-6 bg-primary/10 text-primary hover:bg-primary/20 rounded-xl w-full sm:w-auto"
            onClick={() => navigate("/chat")}
            data-testid="ask-coach-btn"
          >
            Ask Your AI Coach
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>

        {/* Sun Sign Card */}
        <div className="glass-card rounded-xl p-5 lg:p-6 card-lift" data-testid="sun-sign-card">
          <div className="flex items-center justify-between mb-4">
            <Sun className="w-7 lg:w-8 h-7 lg:h-8 text-primary" />
            <span className="zodiac-badge rounded-full px-3 py-1 text-xs">Sun</span>
          </div>
          <p className="font-serif text-xl lg:text-2xl text-foreground mb-1">{user?.sun_sign || "Unknown"}</p>
          <p className="text-xs text-muted-foreground">Your core identity</p>
        </div>

        {/* Quick Stats */}
        <div className="glass-card rounded-xl p-5 lg:p-6 card-lift" data-testid="quick-stats-card">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-500" />
            <span className="text-sm text-green-500 font-medium">Active Transits</span>
          </div>
          <p className="font-serif text-2xl lg:text-3xl text-foreground mb-1">{transits.length}</p>
          <p className="text-xs text-muted-foreground">Influencing your chart</p>
        </div>

        {/* Action Items */}
        <div className="glass-card rounded-xl p-5 lg:p-6 md:col-span-2" data-testid="action-items-card">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-5 h-5 text-primary" />
            <h2 className="font-medium text-foreground">Today's Actions</h2>
          </div>
          <div className="space-y-3">
            {dailyGuidance?.action_items?.map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-5 h-5 rounded-full border border-primary/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-primary/50" />
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{item}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Numerology Quick View */}
        {numerology && (numerology.life_path?.number || numerology.personal_year?.number) && (
          <div className="glass-card rounded-xl p-5 lg:p-6 md:col-span-2 lg:col-span-4" data-testid="numerology-dashboard-card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Hash className="w-5 h-5 text-primary" />
                <h2 className="font-medium text-foreground">Your Numerology</h2>
              </div>
              <Link to="/chart" className="text-xs text-primary hover:text-primary/80 transition-colors flex items-center gap-1">
                Full Profile <ChevronRight className="w-3 h-3" />
              </Link>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { key: "life_path",     label: "Life Path",     icon: "🌟", desc: "Core life mission" },
                { key: "personal_year", label: "Personal Year", icon: "📅", desc: "Your theme this year" },
                { key: "soul_urge",     label: "Soul Urge",     icon: "💜", desc: "What you truly desire" },
                { key: "expression",    label: "Expression",    icon: "📢", desc: "How you manifest" },
              ].map(({ key, label, icon, desc }) => {
                const entry = numerology[key];
                if (!entry?.number) return null;
                const isMaster = [11, 22, 33].includes(entry.number);
                return (
                  <div key={key} className="p-4 rounded-xl bg-muted/30 text-center">
                    <div className="text-xl mb-1">{icon}</div>
                    <div className={`text-2xl font-bold mb-0.5 font-serif ${isMaster ? "text-yellow-400" : "text-primary"}`}>
                      {entry.number}{isMaster && <span className="text-xs ml-0.5">✦</span>}
                    </div>
                    <div className="text-xs font-medium text-foreground">{label}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">{entry.keyword}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Upcoming Transits */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-serif text-lg lg:text-xl text-foreground">Upcoming Transits</h2>
          <Button 
            variant="ghost" 
            className="text-primary"
            onClick={() => navigate("/transits")}
            data-testid="view-all-transits-btn"
          >
            View All
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {transits.map((transit, i) => (
            <div 
              key={transit.id} 
              className="transit-card glass-card rounded-xl p-4 lg:p-5 card-lift"
              data-testid={`transit-card-${i}`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-primary font-medium">{transit.transit_type}</span>
                <span className="text-xs text-muted-foreground">
                  {new Date(transit.peak_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              </div>
              <p className="text-sm text-muted-foreground mb-3 line-clamp-2 leading-relaxed">
                {transit.interpretation}
              </p>
              <div className="flex items-center gap-2">
                <div className="h-1.5 flex-1 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary rounded-full progress-animate"
                    style={{ width: `${transit.strength * 100}%` }}
                  />
                </div>
                <span className="text-xs text-muted-foreground font-mono">{Math.round(transit.strength * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { icon: MessageCircle, label: "Chat", href: "/chat", color: "text-blue-500" },
          { icon: Sun, label: "Chart", href: "/chart", color: "text-amber-500" },
          { icon: Share2, label: "Share", href: "/share", color: "text-purple-500" },
          { icon: Settings, label: "Settings", href: "/settings", color: "text-slate-500" }
        ].map((action) => (
          <Link 
            key={action.label}
            to={action.href}
            className="glass-card rounded-xl p-4 flex flex-col items-center gap-2 card-lift hover:border-primary/30 transition-all"
          >
            <action.icon className={`w-6 h-6 ${action.color}`} />
            <span className="text-sm text-foreground">{action.label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [mobileOpen, setMobileOpen] = useState(false);
  const { token, updateUser } = useAuth();

  // Handle Stripe Checkout success redirect (?subscription=success&tier=...)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("subscription") === "success") {
      const tier = params.get("tier");
      if (tier) updateUser({ subscription_tier: tier });
      // Remove query params from URL without reload
      window.history.replaceState({}, "", window.location.pathname);
      import("sonner").then(({ toast }) => {
        toast.success("🎉 Subscription activated! Welcome to your new plan.");
      });
    }
  }, [updateUser]);

  return (
    <div className="min-h-screen bg-background">
      <MobileHeader setMobileOpen={setMobileOpen} />
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />
      
      <main className="lg:ml-64 p-4 lg:p-8 pt-20 lg:pt-8">
        <DashboardOverview />
      </main>
    </div>
  );
}
