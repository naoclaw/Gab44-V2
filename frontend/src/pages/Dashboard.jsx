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
  Target
} from "lucide-react";

const Sidebar = ({ activeTab, setActiveTab }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const navItems = [
    { id: "overview", icon: BarChart3, label: "Overview" },
    { id: "chat", icon: MessageCircle, label: "AI Coach", href: "/chat" },
    { id: "chart", icon: Sun, label: "Birth Chart", href: "/chart" },
    { id: "transits", icon: Calendar, label: "Transits", href: "/transits" },
  ];

  const handleNavClick = (item) => {
    if (item.href) {
      navigate(item.href);
    } else {
      setActiveTab(item.id);
    }
  };

  return (
    <aside className="w-64 bg-card/50 backdrop-blur-sm border-r border-border flex flex-col h-screen fixed left-0 top-0">
      <div className="p-6 border-b border-border">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <span className="font-serif text-xl text-foreground">Gab44</span>
        </Link>
      </div>

      <nav className="flex-1 p-4">
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
        {/* Theme Toggle */}
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
    </aside>
  );
};

const DashboardOverview = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [dailyGuidance, setDailyGuidance] = useState(null);
  const [transits, setTransits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [guidanceRes, transitsRes] = await Promise.all([
          axios.get(`${API}/guidance/daily`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API}/transits/upcoming`, {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);
        setDailyGuidance(guidanceRes.data);
        setTransits(transitsRes.data.slice(0, 3));
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="glass-card rounded-xl p-6 h-48 skeleton" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="font-serif text-3xl text-foreground mb-2">
          Welcome back, {user?.name?.split(" ")[0]}
        </h1>
        <p className="text-muted-foreground">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Daily Energy - Large */}
        <div className="glass-card rounded-xl p-6 lg:col-span-2 lg:row-span-2" data-testid="daily-energy-card">
          <div className="flex items-center gap-2 mb-4">
            <Sun className="w-5 h-5 text-primary" />
            <h2 className="font-medium text-foreground">Daily Energy</h2>
          </div>
          <p className="text-muted-foreground mb-6 leading-relaxed">
            {dailyGuidance?.overall_energy || "Loading your cosmic guidance..."}
          </p>
          
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-foreground">Focus Areas Today</h3>
            {dailyGuidance?.focus_areas?.map((area, i) => (
              <div key={i} className="flex items-center gap-3 text-sm text-muted-foreground">
                <Target className="w-4 h-4 text-primary flex-shrink-0" />
                {area}
              </div>
            ))}
          </div>

          <Button 
            className="mt-6 bg-primary/10 text-primary hover:bg-primary/20 rounded-xl"
            onClick={() => navigate("/chat")}
            data-testid="ask-coach-btn"
          >
            Ask Your AI Coach
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>

        {/* Sun Sign Card */}
        <div className="glass-card rounded-xl p-6 card-lift" data-testid="sun-sign-card">
          <div className="flex items-center justify-between mb-4">
            <Sun className="w-8 h-8 text-primary" />
            <span className="zodiac-badge rounded-full px-3 py-1 text-xs">Sun</span>
          </div>
          <p className="font-serif text-2xl text-foreground mb-1">{user?.sun_sign || "Unknown"}</p>
          <p className="text-xs text-muted-foreground">Your core identity</p>
        </div>

        {/* Quick Stats */}
        <div className="glass-card rounded-xl p-6 card-lift" data-testid="quick-stats-card">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-500" />
            <span className="text-sm text-green-500 font-medium">Active Transits</span>
          </div>
          <p className="font-serif text-3xl text-foreground mb-1">{transits.length}</p>
          <p className="text-xs text-muted-foreground">Influencing your chart</p>
        </div>

        {/* Action Items */}
        <div className="glass-card rounded-xl p-6 lg:col-span-2" data-testid="action-items-card">
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
      </div>

      {/* Upcoming Transits */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-serif text-xl text-foreground">Upcoming Transits</h2>
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
              className="transit-card glass-card rounded-xl p-5 card-lift"
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
    </div>
  );
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-background">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="ml-64 p-8">
        <DashboardOverview />
      </main>
    </div>
  );
}
