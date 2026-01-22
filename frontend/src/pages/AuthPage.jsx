import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Sparkles, ArrowLeft, Eye, EyeOff, MapPin, Calendar, Clock } from "lucide-react";

export default function AuthPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, login, register } = useAuth();
  
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
    <div className="min-h-screen flex">
      {/* Left Side - Form */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center px-8 md:px-16 lg:px-24 py-12 bg-cosmic-void">
        <button 
          onClick={() => navigate("/")}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-12 w-fit"
          data-testid="back-to-home"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </button>

        <div className="flex items-center gap-2 mb-8">
          <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <span className="font-serif text-xl text-cosmic-starlight">Gab44</span>
        </div>

        <h1 className="font-serif text-3xl md:text-4xl text-cosmic-starlight mb-2">
          {isRegister ? "Create Your Account" : "Welcome Back"}
        </h1>
        <p className="text-muted-foreground mb-8">
          {isRegister 
            ? "Enter your birth details to unlock your cosmic blueprint" 
            : "Sign in to continue your cosmic journey"
          }
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          {isRegister && (
            <>
              <div className="space-y-2">
                <Label htmlFor="name">Full Name *</Label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  placeholder="Your name"
                  value={formData.name}
                  onChange={handleChange}
                  className="bg-black/30 border-white/10 h-12"
                  data-testid="name-input"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="birth_date" className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    Birth Date *
                  </Label>
                  <Input
                    id="birth_date"
                    name="birth_date"
                    type="date"
                    value={formData.birth_date}
                    onChange={handleChange}
                    className="bg-black/30 border-white/10 h-12"
                    data-testid="birth-date-input"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="birth_time" className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    Birth Time
                  </Label>
                  <Input
                    id="birth_time"
                    name="birth_time"
                    type="time"
                    value={formData.birth_time}
                    onChange={handleChange}
                    className="bg-black/30 border-white/10 h-12"
                    data-testid="birth-time-input"
                    placeholder="Optional"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="birth_place" className="flex items-center gap-2">
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
                  className="bg-black/30 border-white/10 h-12"
                  data-testid="birth-place-input"
                  required
                />
              </div>
            </>
          )}

          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="your@email.com"
              value={formData.email}
              onChange={handleChange}
              className="bg-black/30 border-white/10 h-12"
              data-testid="email-input"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                className="bg-black/30 border-white/10 h-12 pr-10"
                data-testid="password-input"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <Button 
            type="submit" 
            className="w-full glow-button bg-primary text-primary-foreground h-12 text-base"
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
            className="text-primary hover:underline"
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
        <div className="absolute inset-0 bg-gradient-to-r from-cosmic-void via-cosmic-void/80 to-transparent" />
        <div className="absolute bottom-12 left-12 right-12">
          <blockquote className="text-lg text-cosmic-starlight italic">
            "The cosmos is within us. We are made of star-stuff. We are a way for the universe to know itself."
          </blockquote>
          <p className="text-muted-foreground mt-2">— Carl Sagan</p>
        </div>
      </div>
    </div>
  );
}
