import { useState, useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTheme } from "@/context/ThemeContext";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Sparkles, ArrowLeft, Eye, EyeOff, MapPin, Calendar, Clock, Sun, Moon, Search, Check } from "lucide-react";

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
    birth_place: "",
    birth_latitude: null,
    birth_longitude: null,
  });

  // City search state
  const [cityQuery, setCityQuery] = useState("");
  const [cityResults, setCityResults] = useState([]);
  const [showCityDropdown, setShowCityDropdown] = useState(false);
  const [cityLoading, setCityLoading] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(-1);
  const cityDropdownRef = useRef(null);
  const cityListRef = useRef(null);

  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  // Search cities when query changes
  useEffect(() => {
    if (!cityQuery || cityQuery.length < 1) {
      setCityResults([]);
      setHighlightIndex(-1);
      return;
    }
    const timer = setTimeout(async () => {
      setCityLoading(true);
      try {
        const res = await axios.get(`${API}/cities`, { params: { q: cityQuery } });
        setCityResults(res.data);
        setHighlightIndex(-1);
      } catch {
        setCityResults([]);
      } finally {
        setCityLoading(false);
      }
    }, 150);
    return () => clearTimeout(timer);
  }, [cityQuery]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (cityDropdownRef.current && !cityDropdownRef.current.contains(e.target)) {
        setShowCityDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selectCity = (city) => {
    const displayName = `${city.name}, ${city.country}`;
    setFormData({
      ...formData,
      birth_place: displayName,
      birth_latitude: city.latitude,
      birth_longitude: city.longitude,
    });
    setCityQuery(displayName);
    setShowCityDropdown(false);
    setHighlightIndex(-1);
  };

  // Keyboard navigation for city dropdown
  const handleCityKeyDown = (e) => {
    if (!showCityDropdown || cityResults.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightIndex((prev) => {
        const next = prev < cityResults.length - 1 ? prev + 1 : 0;
        scrollToItem(next);
        return next;
      });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightIndex((prev) => {
        const next = prev > 0 ? prev - 1 : cityResults.length - 1;
        scrollToItem(next);
        return next;
      });
    } else if (e.key === "Enter" && highlightIndex >= 0) {
      e.preventDefault();
      selectCity(cityResults[highlightIndex]);
    } else if (e.key === "Escape") {
      setShowCityDropdown(false);
      setHighlightIndex(-1);
    }
  };

  const scrollToItem = (index) => {
    if (cityListRef.current) {
      const items = cityListRef.current.querySelectorAll("[data-city-item]");
      if (items[index]) {
        items[index].scrollIntoView({ block: "nearest" });
      }
    }
  };

  // Highlight matching text in city name
  const highlightMatch = (text, query) => {
    if (!query) return text;
    const idx = text.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return text;
    return (
      <>
        {text.slice(0, idx)}
        <span className="text-primary font-semibold">{text.slice(idx, idx + query.length)}</span>
        {text.slice(idx + query.length)}
      </>
    );
  };

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
        if (!formData.birth_latitude) {
          toast.error("Please select a city from the dropdown");
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

              <div className="space-y-2" ref={cityDropdownRef}>
                <Label htmlFor="birth_place" className="flex items-center gap-2 text-foreground">
                  <MapPin className="w-4 h-4 text-muted-foreground" />
                  Birth Place *
                </Label>
                <div className="relative">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                    <Input
                      id="birth_place"
                      type="text"
                      placeholder="Start typing a city name..."
                      value={cityQuery}
                      onChange={(e) => {
                        setCityQuery(e.target.value);
                        setShowCityDropdown(true);
                        // Clear coordinates when user types (they need to re-select)
                        if (formData.birth_latitude) {
                          setFormData({ ...formData, birth_latitude: null, birth_longitude: null });
                        }
                      }}
                      onFocus={() => {
                        if (cityQuery.length >= 1) setShowCityDropdown(true);
                      }}
                      onKeyDown={handleCityKeyDown}
                      className="bg-muted/30 border-border h-12 rounded-xl focus-glow pl-10"
                      data-testid="birth-place-input"
                      autoComplete="off"
                      role="combobox"
                      aria-expanded={showCityDropdown}
                      aria-autocomplete="list"
                    />
                    {formData.birth_latitude && (
                      <Check className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-green-500" />
                    )}
                  </div>

                  {/* City Autocomplete Dropdown */}
                  {showCityDropdown && cityQuery.length >= 1 && (
                    <div 
                      ref={cityListRef}
                      className="absolute z-50 w-full mt-1 bg-card border border-border rounded-xl shadow-lg max-h-60 overflow-y-auto" 
                      data-testid="city-dropdown"
                      role="listbox"
                    >
                      {cityLoading ? (
                        <div className="p-3 text-center text-sm text-muted-foreground">Searching...</div>
                      ) : cityResults.length > 0 ? (
                        <>
                          {cityResults.map((city, idx) => (
                            <button
                              key={`${city.name}-${city.country}`}
                              type="button"
                              data-city-item
                              onClick={() => selectCity(city)}
                              className={`w-full text-left px-4 py-2.5 transition-colors flex items-center justify-between first:rounded-t-xl last:rounded-b-xl ${
                                idx === highlightIndex ? "bg-primary/10" : "hover:bg-muted/50"
                              }`}
                              role="option"
                              aria-selected={idx === highlightIndex}
                              data-testid={`city-option-${city.name.toLowerCase().replace(/\s/g, '-')}`}
                            >
                              <div>
                                <span className="text-sm text-foreground">{highlightMatch(city.name, cityQuery)}</span>
                                <span className="text-sm text-muted-foreground">, {highlightMatch(city.country, cityQuery)}</span>
                              </div>
                              <span className="text-xs text-muted-foreground font-mono ml-2 flex-shrink-0">
                                {city.latitude.toFixed(1)}°, {city.longitude.toFixed(1)}°
                              </span>
                            </button>
                          ))}
                          <div className="px-4 py-1.5 text-xs text-muted-foreground border-t border-border bg-muted/20 rounded-b-xl" aria-label={`${cityResults.length} results. Use up and down arrows to navigate, Enter to select`}>
                            {cityResults.length} result{cityResults.length !== 1 ? "s" : ""} · ↑↓ navigate · Enter select
                          </div>
                        </>
                      ) : (
                        <div className="p-3 text-center text-sm text-muted-foreground">
                          No cities found for "{cityQuery}"
                        </div>
                      )}
                    </div>
                  )}
                </div>
                {formData.birth_latitude && (
                  <p className="text-xs text-muted-foreground">
                    📍 {formData.birth_latitude.toFixed(4)}°, {formData.birth_longitude.toFixed(4)}°
                  </p>
                )}
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
