import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "@/App";
import { useTheme } from "@/context/ThemeContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Sparkles, ArrowLeft, Eye, EyeOff, MapPin, Calendar, Clock, Sun, Moon } from "lucide-react";

export default function AuthPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, login, register } = useAuth();
  const { theme, toggleTheme } = useTheme();
  
  const [isRegister, setIsRegister] = useState(searchParams.get("mode") === "register");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
    birth_date: "",
    birth_time: "",
    birth_place: ""
  });

  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isRegister) {
        if (!formData.name || !formData.birth_date || !formData.birth_place) {
          toast.error("Please fill in all required fields");
          setLoading(false);
          return;
        }
        await register(formData);
        toast.success("Welcome to Gab44! Your cosmic journey begins now.");
      } else {
        await login(formData.email, formData.password);
        toast.success("Welcome back! The stars have been waiting.");
      }
      navigate("/dashboard");
    } catch (error) {
      const message = error.response?.data?.detail || "Something went wrong";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-background">
      {/* Left Side - Form */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center px-8 md:px-16 lg:px-24 py-12">
        <div className="flex items-center justify-between mb-12">
          <button 
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            data-testid="back-to-home"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="w-10 h-10 rounded-xl bg-muted/50 hover:bg-muted flex items-center justify-center transition-colors border border-border/50"
            aria-label="Toggle theme"
          >
            {theme === "dark" ? <Sun className="w-5 h-5 text-primary" /> : <Moon className="w-5 h-5 text-muted-foreground" />}
          </button>
        </div>

        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <span className="font-serif text-xl text-foreground">Gab44</span>
        </div>

        <h1 className="font-serif text-3xl md:text-4xl text-foreground mb-2">
          {isRegister ? "Create Your Account" : "Welcome Back"}
        </h1>
        <p className="text-muted-foreground mb-8 leading-relaxed">
          {isRegister 
            ? "Enter your birth details to unlock your cosmic blueprint" 
            : "Sign in to continue your cosmic journey"
          }
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          {isRegister && (
            <>
              <div className="space-y-2">
                <Label htmlFor="name" className="text-foreground">Full Name *</Label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  placeholder="Your name"
                  value={formData.name}
                  onChange={handleChange}
                  className="bg-muted/30 border-border h-12 rounded-xl focus-glow"
                  data-testid="name-input"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="birth_date" className="flex items-center gap-2 text-foreground">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    Birth Date *
                  </Label>
                  <Input
                    id="birth_date"
                    name="birth_date"
                    type="date"
                    value={formData.birth_date}
                    onChange={handleChange}
                    className="bg-muted/30 border-border h-12 rounded-xl focus-glow"
                    data-testid="birth-date-input"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="birth_time" className="flex items-center gap-2 text-foreground">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    Birth Time
                  </Label>
                  <Input
                    id="birth_time"
                    name="birth_time"
                    type="time"
                    value={formData.birth_time}
                    onChange={handleChange}
                    className="bg-muted/30 border-border h-12 rounded-xl focus-glow"
                    data-testid="birth-time-input"
                    placeholder="Optional"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="birth_place" className="flex items-center gap-2 text-foreground">
                  <MapPin className="w-4 h-4 text-muted-foreground" />
                  Birth Place *
                </Label>
                <Input
                  id="birth_place"
                  name="birth_place"
                  type="text"
                  placeholder="City, Country"
                  value={formData.birth_place}
                  onChange={handleChange}
                  className="bg-muted/30 border-border h-12 rounded-xl focus-glow"
                  data-testid="birth-place-input"
                  required
                />
              </div>
            </>
          )}

          <div className="space-y-2">
            <Label htmlFor="email" className="text-foreground">Email Address</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="your@email.com"
              value={formData.email}
              onChange={handleChange}
              className="bg-muted/30 border-border h-12 rounded-xl focus-glow"
              data-testid="email-input"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-foreground">Password</Label>
            <div className="relative">
              <Input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                className="bg-muted/30 border-border h-12 rounded-xl pr-10 focus-glow"
                data-testid="password-input"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <Button 
            type="submit" 
            className="w-full glow-button bg-primary text-primary-foreground h-12 text-base rounded-xl"
            disabled={loading}
            data-testid="submit-btn"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                {isRegister ? "Creating Your Chart..." : "Signing In..."}
              </span>
            ) : (
              isRegister ? "Create Your Free Chart" : "Sign In"
            )}
          </Button>
        </form>

        <p className="text-sm text-muted-foreground mt-6 text-center">
          {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            onClick={() => setIsRegister(!isRegister)}
            className="text-primary hover:underline font-medium"
            data-testid="toggle-auth-mode"
          >
            {isRegister ? "Sign In" : "Create One"}
          </button>
        </p>
      </div>

      {/* Right Side - Image */}
      <div 
        className="hidden lg:block lg:w-1/2 bg-cover bg-center relative"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1465101162946-4377e57745c3?q=80&w=1200')`
        }}
      >
        <div className={`absolute inset-0 ${theme === 'dark' ? 'bg-gradient-to-r from-background via-background/80 to-transparent' : 'bg-gradient-to-r from-background via-background/90 to-background/30'}`} />
        <div className="absolute bottom-12 left-12 right-12">
          <blockquote className="text-lg text-foreground italic leading-relaxed">
            "The cosmos is within us. We are made of star-stuff. We are a way for the universe to know itself."
          </blockquote>
          <p className="text-muted-foreground mt-3">— Carl Sagan</p>
        </div>
      </div>
    </div>
  );
}
