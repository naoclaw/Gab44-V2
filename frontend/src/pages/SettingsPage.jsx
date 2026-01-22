import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTheme } from "@/context/ThemeContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { toast } from "sonner";
import { 
  ArrowLeft, 
  User, 
  Sun, 
  Moon, 
  Sparkles,
  Settings2,
  Bell,
  Shield,
  CreditCard,
  Type,
  Eye,
  Save,
  LogOut
} from "lucide-react";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  
  const [fontSize, setFontSize] = useState(() => {
    const stored = localStorage.getItem("gab44_font_size");
    return stored ? parseInt(stored) : 16;
  });
  
  const [readingMode, setReadingMode] = useState(() => {
    return localStorage.getItem("gab44_reading_mode") === "true";
  });

  const [notifications, setNotifications] = useState({
    dailyGuidance: true,
    transitAlerts: true,
    weeklyReport: false,
    marketing: false
  });

  const handleFontSizeChange = (value) => {
    setFontSize(value[0]);
    localStorage.setItem("gab44_font_size", value[0].toString());
    document.documentElement.style.setProperty("--base-font-size", `${value[0]}px`);
  };

  const handleReadingModeToggle = (checked) => {
    setReadingMode(checked);
    localStorage.setItem("gab44_reading_mode", checked.toString());
    const root = document.documentElement;
    if (checked) {
      root.style.setProperty("--reading-line-height", "1.9");
      root.style.setProperty("--reading-letter-spacing", "0.02em");
    } else {
      root.style.setProperty("--reading-line-height", "1.7");
      root.style.setProperty("--reading-letter-spacing", "0.01em");
    }
    toast.success(checked ? "Reading mode enabled" : "Reading mode disabled");
  };

  const settingsSections = [
    {
      id: "appearance",
      title: "Appearance",
      icon: Eye,
      content: (
        <div className="space-y-6">
          {/* Theme Toggle */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-foreground">Theme</Label>
              <p className="text-sm text-muted-foreground">Choose light or dark mode</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleTheme}
              className="gap-2 rounded-xl"
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              {theme === "dark" ? "Light" : "Dark"}
            </Button>
          </div>

          {/* Reading Mode */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-foreground">Reading Mode</Label>
              <p className="text-sm text-muted-foreground">Increase spacing for easier reading</p>
            </div>
            <Switch
              checked={readingMode}
              onCheckedChange={handleReadingModeToggle}
              data-testid="reading-mode-toggle"
            />
          </div>

          {/* Font Size */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="text-foreground">Font Size</Label>
                <p className="text-sm text-muted-foreground">Adjust text size ({fontSize}px)</p>
              </div>
              <Type className="w-5 h-5 text-muted-foreground" />
            </div>
            <Slider
              value={[fontSize]}
              onValueChange={handleFontSizeChange}
              min={12}
              max={24}
              step={1}
              className="w-full"
              data-testid="font-size-slider"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Small</span>
              <span>Default</span>
              <span>Large</span>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "notifications",
      title: "Notifications",
      icon: Bell,
      content: (
        <div className="space-y-4">
          {[
            { key: "dailyGuidance", label: "Daily Guidance", desc: "Receive your daily cosmic insights" },
            { key: "transitAlerts", label: "Transit Alerts", desc: "Get notified about important transits" },
            { key: "weeklyReport", label: "Weekly Report", desc: "Summary of the week ahead" },
            { key: "marketing", label: "Updates & Offers", desc: "News about new features and promotions" }
          ].map(({ key, label, desc }) => (
            <div key={key} className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="text-foreground">{label}</Label>
                <p className="text-sm text-muted-foreground">{desc}</p>
              </div>
              <Switch
                checked={notifications[key]}
                onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, [key]: checked }))}
              />
            </div>
          ))}
        </div>
      )
    },
    {
      id: "account",
      title: "Account",
      icon: User,
      content: (
        <div className="space-y-4">
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center font-serif text-2xl text-primary">
                {user?.name?.[0] || "U"}
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-foreground">{user?.name}</h3>
                <p className="text-sm text-muted-foreground">{user?.email}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="zodiac-badge rounded-full px-2 py-0.5 text-xs">{user?.sun_sign}</span>
                  <span className="text-xs text-muted-foreground">Born {user?.birth_date}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-foreground">Birth Place</Label>
            <Input value={user?.birth_place || ""} disabled className="bg-muted/30 rounded-xl" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-foreground">Birth Date</Label>
              <Input value={user?.birth_date || ""} disabled className="bg-muted/30 rounded-xl" />
            </div>
            <div className="space-y-2">
              <Label className="text-foreground">Birth Time</Label>
              <Input value={user?.birth_time || "Not provided"} disabled className="bg-muted/30 rounded-xl" />
            </div>
          </div>
        </div>
      )
    },
    {
      id: "subscription",
      title: "Subscription",
      icon: CreditCard,
      content: (
        <div className="space-y-4">
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-medium text-foreground capitalize">{user?.subscription_tier || "Seeker"} Plan</h3>
                <p className="text-sm text-muted-foreground">
                  {user?.subscription_tier === "seeker" ? "Free forever" : "Billed monthly"}
                </p>
              </div>
              <Sparkles className="w-6 h-6 text-primary" />
            </div>
            <Button 
              onClick={() => navigate("/pricing")}
              className="w-full bg-primary/10 text-primary hover:bg-primary/20 rounded-xl"
            >
              {user?.subscription_tier === "seeker" ? "Upgrade Plan" : "Manage Subscription"}
            </Button>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link to="/dashboard" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-4">
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back to Dashboard</span>
            </Link>
            <h1 className="font-serif text-3xl text-foreground">Settings</h1>
            <p className="text-muted-foreground">Customize your Gab44 experience</p>
          </div>
          <Settings2 className="w-8 h-8 text-muted-foreground" />
        </div>

        {/* Settings Sections */}
        <div className="space-y-6">
          {settingsSections.map((section) => (
            <div key={section.id} className="glass-card rounded-xl p-6" data-testid={`settings-${section.id}`}>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                  <section.icon className="w-5 h-5 text-primary" />
                </div>
                <h2 className="font-medium text-foreground text-lg">{section.title}</h2>
              </div>
              {section.content}
            </div>
          ))}

          {/* Danger Zone */}
          <div className="glass-card rounded-xl p-6 border-destructive/20">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-destructive/10 flex items-center justify-center">
                <Shield className="w-5 h-5 text-destructive" />
              </div>
              <h2 className="font-medium text-foreground text-lg">Account Actions</h2>
            </div>
            <Button 
              variant="outline" 
              className="w-full border-destructive/30 text-destructive hover:bg-destructive/10 rounded-xl"
              onClick={() => {
                logout();
                navigate("/");
              }}
              data-testid="logout-settings"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
