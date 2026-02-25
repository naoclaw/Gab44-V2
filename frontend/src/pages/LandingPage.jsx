import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth, API } from "@/App";
import { useTheme } from "@/context/ThemeContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Sparkles, 
  Star, 
  Moon, 
  Sun, 
  ArrowRight, 
  Check, 
  MessageCircle,
  BarChart3,
  Calendar,
  Shield,
  Zap,
  Users,
  Menu,
  X,
  Mail,
  Send,
  Heart,
  Hash,
  Lock
} from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

// Chaldean gematria cipher (ancient Babylonian, values 1–8; 9 is sacred/excluded)
const CHALDEAN = {
  a:1,b:2,c:3,d:4,e:5,f:8,g:3,h:5,i:1,j:1,k:2,l:3,m:4,
  n:5,o:7,p:8,q:1,r:2,s:3,t:4,u:6,v:6,w:6,x:5,y:1,z:7
};
// Master numbers (11, 22, 33) are never reduced in Chaldean gematria
function chaldeanReduce(n) {
  while (n > 9 && ![11, 22, 33].includes(n)) {
    n = String(n).split("").reduce((s, d) => s + Number(d), 0);
  }
  return n;
}
function computeLandingGematria(text) {
  const clean = text.toLowerCase().replace(/[^a-z]/g, "");
  if (!clean) return null;
  const letters = clean.split("").map(c => ({ letter: c.toUpperCase(), value: CHALDEAN[c] || 0 }));
  const total = letters.reduce((s, l) => s + l.value, 0);
  return { letters, total, reduced: chaldeanReduce(total) };
}

const Navigation = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 glass-header ${scrolled ? 'scrolled' : ''}`}>
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="nav-logo">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center border border-primary/20 shadow-sm">
              <Sparkles className="w-5 h-5 text-primary" />
            </div>
            <span className="font-serif text-xl font-semibold text-foreground">Gab44</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="nav-link text-sm text-muted-foreground hover:text-foreground link-hover">Features</a>
            <a href="#testimonials" className="nav-link text-sm text-muted-foreground hover:text-foreground link-hover">Testimonials</a>
            <a href="#gematria" className="nav-link text-sm text-muted-foreground hover:text-foreground link-hover">Gematria</a>
            <a href="#pricing" className="nav-link text-sm text-muted-foreground hover:text-foreground link-hover">Pricing</a>
            <a href="#faq" className="nav-link text-sm text-muted-foreground hover:text-foreground link-hover">FAQ</a>
            <a href="#contact" className="nav-link text-sm text-muted-foreground hover:text-foreground link-hover">Contact</a>
          </div>

          <div className="hidden md:flex items-center gap-3">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="w-10 h-10 rounded-xl bg-muted/50 hover:bg-muted flex items-center justify-center transition-colors border border-border/50"
              data-testid="theme-toggle"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? (
                <Sun className="w-5 h-5 text-primary" />
              ) : (
                <Moon className="w-5 h-5 text-muted-foreground" />
              )}
            </button>

            {user ? (
              <>
                <Button 
                  variant="ghost" 
                  onClick={() => navigate("/dashboard")}
                  data-testid="nav-dashboard-btn"
                  className="text-foreground"
                >
                  Dashboard
                </Button>
                <Button 
                  variant="outline" 
                  onClick={logout}
                  data-testid="nav-logout-btn"
                  className="border-border"
                >
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                <Button 
                  variant="ghost" 
                  onClick={() => navigate("/auth")}
                  data-testid="nav-login-btn"
                  className="text-foreground"
                >
                  Sign In
                </Button>
                <Button 
                  onClick={() => navigate("/auth?mode=register")}
                  data-testid="nav-register-btn"
                  className="glow-button bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  Get Started
                </Button>
              </>
            )}
          </div>

          {/* Mobile controls */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={toggleTheme}
              className="w-10 h-10 rounded-xl bg-muted/50 flex items-center justify-center"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <Sun className="w-5 h-5 text-primary" /> : <Moon className="w-5 h-5" />}
            </button>
            <button 
              className="w-10 h-10 rounded-xl bg-muted/50 flex items-center justify-center"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-menu-btn"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-border pt-4 space-y-4">
            <a href="#features" className="block text-muted-foreground hover:text-foreground py-2">Features</a>
            <a href="#testimonials" className="block text-muted-foreground hover:text-foreground py-2">Testimonials</a>
            <a href="#gematria" className="block text-muted-foreground hover:text-foreground py-2">Gematria</a>
            <a href="#pricing" className="block text-muted-foreground hover:text-foreground py-2">Pricing</a>
            <a href="#faq" className="block text-muted-foreground hover:text-foreground py-2">FAQ</a>
            <a href="#contact" className="block text-muted-foreground hover:text-foreground py-2">Contact</a>
            <div className="flex gap-2 pt-2">
              {user ? (
                <Button onClick={() => navigate("/dashboard")} className="flex-1 bg-primary">Dashboard</Button>
              ) : (
                <>
                  <Button variant="outline" onClick={() => navigate("/auth")} className="flex-1">Sign In</Button>
                  <Button onClick={() => navigate("/auth?mode=register")} className="flex-1 bg-primary">Get Started</Button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

const HeroSection = () => {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const [birthDate, setBirthDate] = useState("");
  const [sunSign, setSunSign] = useState(null);

  const SUN_SIGN_TRAITS = {
    Aries: ["Natural leader, fearless trailblazer", "Driven by passion and independence", "Thrives on challenge and new beginnings"],
    Taurus: ["Grounded builder, sensory connoisseur", "Values stability, loyalty, and beauty", "Patient determination that moves mountains"],
    Gemini: ["Quick-witted communicator, eternal student", "Thrives on variety and intellectual connection", "Adaptable mind that bridges worlds"],
    Cancer: ["Intuitive nurturer, emotional depth", "Fierce protector of loved ones", "Deep connection to home and heritage"],
    Leo: ["Radiant creator, natural performer", "Generous heart with magnetic presence", "Born to inspire and lead with warmth"],
    Virgo: ["Precise analyst, devoted healer", "Eye for detail that others miss", "Service-oriented with quiet strength"],
    Libra: ["Harmonizer, aesthetic visionary", "Seeks balance, justice, and beauty", "Natural diplomat with graceful charm"],
    Scorpio: ["Intense transformer, truth-seeker", "Emotional depth that sees through surfaces", "Power through vulnerability and rebirth"],
    Sagittarius: ["Adventurous philosopher, freedom-seeker", "Expansive vision that sees the big picture", "Natural teacher with infectious optimism"],
    Capricorn: ["Strategic builder, patient achiever", "Quiet authority that commands respect", "Long-term vision with disciplined execution"],
    Aquarius: ["Visionary rebel, humanitarian innovator", "Thinks decades ahead of the crowd", "Values authenticity and collective progress"],
    Pisces: ["Empathic dreamer, spiritual antenna", "Boundless imagination and compassion", "Feels what others can't articulate"],
  };

  const calculateSunSign = () => {
    if (!birthDate) return;
    const date = new Date(birthDate);
    const month = date.getMonth() + 1;
    const day = date.getDate();

    const signs = [
      { start: [3, 21], end: [4, 19], sign: "Aries" },
      { start: [4, 20], end: [5, 20], sign: "Taurus" },
      { start: [5, 21], end: [6, 20], sign: "Gemini" },
      { start: [6, 21], end: [7, 22], sign: "Cancer" },
      { start: [7, 23], end: [8, 22], sign: "Leo" },
      { start: [8, 23], end: [9, 22], sign: "Virgo" },
      { start: [9, 23], end: [10, 22], sign: "Libra" },
      { start: [10, 23], end: [11, 21], sign: "Scorpio" },
      { start: [11, 22], end: [12, 21], sign: "Sagittarius" },
      { start: [12, 22], end: [1, 19], sign: "Capricorn" },
      { start: [1, 20], end: [2, 18], sign: "Aquarius" },
      { start: [2, 19], end: [3, 20], sign: "Pisces" },
    ];

    for (const { start, end, sign } of signs) {
      if (
        (month === start[0] && day >= start[1]) ||
        (month === end[0] && day <= end[1]) ||
        (start[0] === 12 && month === 12 && day >= start[1]) ||
        (start[0] === 12 && month === 1 && day <= end[1])
      ) {
        setSunSign(sign);
        return;
      }
    }
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?q=80&w=2000')`
        }}
      />
      <div className={`absolute inset-0 ${theme === 'dark' ? 'hero-gradient-dark' : 'hero-gradient-light'}`} />
      <div className="absolute inset-0 cosmic-gradient" />
      
      {/* Floating elements */}
      <div className="absolute top-1/4 left-10 w-2 h-2 rounded-full bg-primary/50 animate-float" style={{ animationDelay: '0s' }} />
      <div className="absolute top-1/3 right-20 w-1.5 h-1.5 rounded-full bg-chart-2/50 animate-float" style={{ animationDelay: '1s' }} />
      <div className="absolute bottom-1/3 left-1/4 w-1 h-1 rounded-full bg-foreground/30 animate-float" style={{ animationDelay: '2s' }} />

      <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
        <p className="text-primary font-semibold mb-4 fade-in tracking-widest text-sm uppercase">
          Your Birth Chart. Decoded.
        </p>
        
        <h1 className="font-serif text-5xl md:text-7xl lg:text-8xl font-semibold text-foreground mb-6 fade-in fade-in-delay-1 hero-title">
          The Stars Know You. <br />
          <span className="gradient-text">Now You Can Know Them.</span>
        </h1>
        
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 fade-in fade-in-delay-2 leading-relaxed">
          Enter your birth details and receive a detailed, AI-interpreted chart covering your personality, 
          relationships, career timing, and life purpose — calculated to astronomical precision.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 fade-in fade-in-delay-3">
          <Button 
            size="lg" 
            onClick={() => navigate("/auth?mode=register")}
            data-testid="hero-cta-btn"
            className="glow-button bg-primary text-primary-foreground hover:bg-primary/90 text-base px-8 py-6 rounded-xl"
          >
            Create Your Free Chart
            <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
          <Button 
            size="lg" 
            variant="outline"
            onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}
            data-testid="hero-features-btn"
            className="border-border hover:bg-muted text-base px-8 py-6 rounded-xl"
          >
            Explore Features
          </Button>
        </div>

        {/* Quick Sign Calculator */}
        <div className="glass-card rounded-2xl p-6 md:p-8 max-w-md mx-auto fade-in fade-in-delay-4">
          <h3 className="font-serif text-lg mb-4 text-foreground">What's Your Cosmic Blueprint?</h3>
          <p className="text-sm text-muted-foreground mb-4">Enter your birth date to reveal your Sun Sign archetype.</p>
          
          <div className="flex gap-3">
            <Input
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              className="flex-1 bg-background/50 border-border h-12 rounded-xl"
              data-testid="birth-date-input"
            />
            <Button 
              onClick={calculateSunSign}
              data-testid="reveal-sign-btn"
              className="bg-primary text-primary-foreground px-6 rounded-xl"
            >
              Reveal
            </Button>
          </div>

          {sunSign && (
            <div className="mt-6 p-4 rounded-xl bg-primary/10 border border-primary/20">
              <p className="text-sm text-muted-foreground">Your Sun Sign</p>
              <p className="font-serif text-2xl text-primary mb-3" data-testid="sun-sign-result">{sunSign}</p>
              <ul className="space-y-1.5 mb-4">
                {(SUN_SIGN_TRAITS[sunSign] || []).map((trait, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <Star className="w-3.5 h-3.5 text-primary mt-0.5 flex-shrink-0" />
                    {trait}
                  </li>
                ))}
              </ul>
              <p className="text-xs text-muted-foreground mb-2">Your full chart has 40+ more data points — planets, houses, aspects, numerology.</p>
              <Button 
                size="sm"
                onClick={() => navigate("/auth?mode=register")}
                className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg text-xs"
              >
                Get Your Full Chart Free
                <ArrowRight className="ml-1 w-3.5 h-3.5" />
              </Button>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="flex flex-wrap justify-center gap-8 md:gap-16 mt-16 fade-in fade-in-delay-5">
          <div className="text-center">
            <p className="font-serif text-3xl md:text-4xl text-foreground stat-number">10k+</p>
            <p className="text-sm text-muted-foreground">Charts Generated</p>
          </div>
          <div className="text-center">
            <p className="font-serif text-3xl md:text-4xl text-foreground stat-number">40+</p>
            <p className="text-sm text-muted-foreground">Data Points Per Chart</p>
          </div>
          <div className="text-center">
            <p className="font-serif text-3xl md:text-4xl text-foreground stat-number">24/7</p>
            <p className="text-sm text-muted-foreground">AI Companion</p>
          </div>
        </div>
      </div>
    </section>
  );
};

const FeaturesSection = () => {
  const features = [
    {
      icon: MessageCircle,
      title: "AI Coaching",
      description: "Receive daily personalized guidance that adapts to your tone, age, and cultural background. Your AI coach learns from you to provide deeper insights over time.",
      image: "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?q=80&w=800"
    },
    {
      icon: BarChart3,
      title: "Deep Analysis",
      description: "Go beyond basic horoscopes with detailed reports on health, relationships, wealth, and career. Based on precise astronomical calculations, not guesswork.",
      image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=800"
    },
    {
      icon: Sparkles,
      title: "Spiritual Growth",
      description: "Uncover your life's purpose and navigate transitions with confidence. We prioritize truthfulness over comfort to help you align with your sacred mission.",
      image: "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=800"
    }
  ];

  const lifeAreas = [
    { icon: Shield, title: "Health & Vitality", description: "Understand your physical constitution and optimal health practices based on your chart." },
    { icon: Users, title: "Relationships & Compatibility", description: "Navigate emotional patterns and deepen connections with partners, family, and friends." },
    { icon: Zap, title: "Career & Wealth", description: "Identify your professional strengths and optimal timing for financial decisions." }
  ];

  return (
    <section id="features" className="py-24 px-6 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-primary font-semibold mb-3 tracking-widest text-sm uppercase">Holistic Guidance</p>
          <h2 className="font-serif text-foreground mb-4">
            Ancient Wisdom Meets Modern AI
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Our platform combines ancient wisdom with modern AI to provide comprehensive insights into every aspect of your life.
          </p>
        </div>

        {/* Main Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-20">
          {features.map((feature, index) => (
            <div 
              key={feature.title} 
              className="feature-card rounded-2xl overflow-hidden group card-lift"
              data-testid={`feature-card-${index}`}
            >
              <div className="aspect-video overflow-hidden">
                <img 
                  src={feature.image} 
                  alt={feature.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>
              <div className="p-6">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-serif text-xl text-foreground mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Life Areas */}
        <div className="text-center mb-12">
          <h3 className="font-serif text-foreground mb-4">Comprehensive Life Guidance</h3>
          <p className="text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Our platform doesn't just look at the stars; it looks at how they influence every tangible aspect of your daily life.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {lifeAreas.map((area, index) => (
            <div 
              key={area.title}
              className="glass-card rounded-xl p-6 card-lift"
              data-testid={`life-area-${index}`}
            >
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <area.icon className="w-5 h-5 text-primary" />
              </div>
              <h4 className="font-medium text-foreground mb-2">{area.title}</h4>
              <p className="text-sm text-muted-foreground leading-relaxed">{area.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const ChatPreview = () => {
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-primary font-semibold mb-3 tracking-widest text-sm uppercase">Two AI Companions</p>
          <h2 className="font-serif text-foreground mb-4">
            A Coach for Direction. A Friend for Everything Else.
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Sometimes you need guidance. Sometimes you just need someone to listen. Gab44 gives you both.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* AI Coach Preview */}
          <div className="glass-card rounded-2xl p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="font-medium text-foreground">Gab44 Coach</p>
                <p className="text-xs text-green-500 flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500" />
                  Guiding your path
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="chat-bubble-assistant rounded-2xl rounded-tl-sm p-3 max-w-xs">
                <p className="text-sm text-foreground leading-relaxed">
                  Mercury is activating your career sector today. It's an excellent time for clear communication.
                </p>
              </div>
              <div className="chat-bubble-user rounded-2xl rounded-tr-sm p-3 max-w-[200px] ml-auto">
                <p className="text-sm text-foreground">
                  I've been feeling stuck lately.
                </p>
              </div>
              <div className="chat-bubble-assistant rounded-2xl rounded-tl-sm p-3 max-w-xs">
                <p className="text-sm text-foreground leading-relaxed">
                  Saturn squaring your Mars is inviting you to restructure. Let's look at where you can simplify...
                </p>
              </div>
            </div>
          </div>

          {/* AI Friend Preview */}
          <div className="glass-card rounded-2xl p-6 md:p-8 friend-preview-card">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-rose-500/15 flex items-center justify-center">
                <Heart className="w-5 h-5 text-rose-400" />
              </div>
              <div>
                <p className="font-medium text-foreground">Saoul</p>
                <p className="text-xs text-rose-400 flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-rose-400" />
                  Always here for you
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="chat-bubble-user rounded-2xl rounded-tr-sm p-3 max-w-[200px] ml-auto">
                <p className="text-sm text-foreground">
                  I can't sleep. Just thinking too much.
                </p>
              </div>
              <div className="chat-bubble-friend rounded-2xl rounded-tl-sm p-3 max-w-xs">
                <p className="text-sm text-foreground leading-relaxed">
                  I'm here. What's on your mind? Sometimes just saying it out loud helps.
                </p>
              </div>
              <div className="chat-bubble-user rounded-2xl rounded-tr-sm p-3 max-w-[200px] ml-auto">
                <p className="text-sm text-foreground">
                  Just feeling lonely honestly.
                </p>
              </div>
              <div className="chat-bubble-friend rounded-2xl rounded-tl-sm p-3 max-w-xs">
                <p className="text-sm text-foreground leading-relaxed">
                  I hear you. That's real, and it takes courage to say it. You're not alone right now though — I'm right here.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

const TestimonialsSection = () => {
  const testimonials = [
    {
      name: "David K.",
      role: "Software Engineer",
      initial: "D",
      content: "Gab44 helped me understand patterns in my life that I couldn't see before. The AI interpretations are surprisingly accurate and non-judgmental. It's like having a wise friend who truly understands your cosmic blueprint."
    },
    {
      name: "Sarah M.",
      role: "Life Coach",
      initial: "S",
      content: "The depth of insight is remarkable. Gab44 doesn't just tell you your sun sign—it reveals the intricate web of planetary influences shaping your journey. A game-changer for self-discovery."
    },
    {
      name: "Michael R.",
      role: "Entrepreneur",
      initial: "M",
      content: "I was skeptical at first, but the timing recommendations for business decisions have been uncannily accurate. Gab44 combines ancient wisdom with practical guidance."
    }
  ];

  return (
    <section id="testimonials" className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-primary font-semibold mb-3 tracking-widest text-sm uppercase">Testimonials</p>
          <h2 className="font-serif text-foreground">
            Trusted by Seekers Worldwide
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <div 
              key={testimonial.name}
              className="testimonial-card glass-card rounded-2xl p-6 card-lift"
              data-testid={`testimonial-${index}`}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center font-serif text-lg text-primary">
                  {testimonial.initial}
                </div>
                <div>
                  <p className="font-medium text-foreground">{testimonial.name}</p>
                  <p className="text-xs text-muted-foreground">{testimonial.role}</p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed italic">
                "{testimonial.content}"
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const PricingSection = () => {
  const navigate = useNavigate();
  
  const plans = [
    {
      name: "Seeker",
      tagline: "For those just starting their journey",
      price: 0,
      features: [
        "Basic Chart Overview",
        "Daily Short Guidance",
        "1 Compatibility Reading",
        "Educational Library"
      ],
      cta: "Create Your Free Chart",
      popular: false
    },
    {
      name: "Enthusiast",
      tagline: "For daily guidance and deeper insights",
      price: 9.99,
      features: [
        "Everything in Seeker",
        "Daily AI Coaching",
        "Monthly Detailed Reports",
        "Unlimited Compatibility",
        "30-Day Transit Forecasts"
      ],
      cta: "Start Free Trial",
      popular: true
    },
    {
      name: "Advanced",
      tagline: "For serious practitioners and coaches",
      price: 29.99,
      features: [
        "Everything in Enthusiast",
        "Advanced Predictive Tools",
        "90-Day Transit Forecasts",
        "Chart Pattern Analysis",
        "Export to PDF"
      ],
      cta: "Upgrade Now",
      popular: false
    }
  ];

  return (
    <section id="pricing" className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-primary font-semibold mb-3 tracking-widest text-sm uppercase">Pricing</p>
          <h2 className="font-serif text-foreground mb-4">
            Choose Your Path
          </h2>
          <p className="text-muted-foreground">
            Flexible plans designed to meet you wherever you are on your journey.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((plan, index) => (
            <div 
              key={plan.name}
              className={`glass-card rounded-2xl p-6 relative card-lift ${plan.popular ? 'pricing-popular' : ''}`}
              data-testid={`pricing-plan-${index}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-xs font-semibold px-4 py-1.5 rounded-full">
                  Most Popular
                </div>
              )}
              
              <h3 className="font-serif text-xl text-foreground mb-1">{plan.name}</h3>
              <p className="text-sm text-muted-foreground mb-6">{plan.tagline}</p>
              
              <div className="mb-6">
                <span className="font-serif text-4xl text-foreground">${plan.price}</span>
                <span className="text-muted-foreground">/month</span>
              </div>

              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <Check className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>

              <Button 
                className={`w-full rounded-xl ${plan.popular ? 'glow-button bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'}`}
                onClick={() => navigate("/auth?mode=register")}
                data-testid={`pricing-cta-${index}`}
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const FAQSection = () => {
  const faqs = [
    {
      question: "How accurate is the astrology data?",
      answer: "We use Swiss Ephemeris, the gold standard in astronomical calculations used by professional astrologers worldwide. Our AI interprets this data with nuance and personalization, resulting in highly accurate and relevant insights."
    },
    {
      question: "Do I need my exact birth time?",
      answer: "While your exact birth time provides the most accurate chart (especially for your rising sign and houses), you can still get valuable insights from your sun and moon signs with just your birth date. We recommend getting your birth certificate for the most complete reading."
    },
    {
      question: "Is this compatible with my religion?",
      answer: "Gab44 approaches astrology as a tool for self-understanding, not as a belief system. Many users of various faiths find value in the psychological and timing insights while maintaining their religious practices."
    },
    {
      question: "Can I cancel my subscription?",
      answer: "Absolutely. You can cancel your subscription at any time from your account settings. Your access continues until the end of your billing period, and you can always return later."
    }
  ];

  return (
    <section id="faq" className="py-24 px-6">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-primary font-semibold mb-3 tracking-widest text-sm uppercase">FAQ</p>
          <h2 className="font-serif text-foreground">
            Frequently Asked Questions
          </h2>
        </div>

        <Accordion type="single" collapsible className="space-y-4">
          {faqs.map((faq, index) => (
            <AccordionItem 
              key={index} 
              value={`item-${index}`}
              className="glass-card rounded-xl px-6 border-none"
              data-testid={`faq-item-${index}`}
            >
              <AccordionTrigger className="text-left font-medium text-foreground hover:no-underline py-6">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground pb-6 leading-relaxed">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
};

const CTASection = () => {
  const navigate = useNavigate();

  return (
    <section className="py-24 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-t from-primary/5 via-transparent to-transparent" />
      
      <div className="max-w-4xl mx-auto text-center relative z-10">
        <h2 className="font-serif text-foreground mb-6">
          Your Chart Is Waiting
        </h2>
        <p className="text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
          40+ data points about your personality, relationships, career, and purpose — calculated to astronomical precision with Swiss Ephemeris and interpreted by AI that actually understands you.
        </p>
        <Button 
          size="lg"
          onClick={() => navigate("/auth?mode=register")}
          data-testid="cta-final-btn"
          className="glow-button bg-primary text-primary-foreground hover:bg-primary/90 text-base px-8 py-6 rounded-xl"
        >
          Create Your Free Chart
          <ArrowRight className="ml-2 w-5 h-5" />
        </Button>
        <div className="flex items-center justify-center gap-2 mt-4 text-xs text-muted-foreground">
          <Lock className="w-3.5 h-3.5" />
          <span>Your data is encrypted and never shared with third parties</span>
        </div>
      </div>
    </section>
  );
};

const GematriaSection = () => {
  const navigate = useNavigate();
  const [input, setInput] = useState("Your Name");
  const [result, setResult] = useState(() => computeLandingGematria("Your Name"));

  const analyse = (val) => {
    setInput(val);
    setResult(computeLandingGematria(val));
  };

  const NUMBER_THEMES = {
    1: "Leadership · Independence · Originality",
    2: "Partnership · Sensitivity · Diplomacy",
    3: "Creativity · Expression · Joy",
    4: "Structure · Stability · Hard Work",
    5: "Freedom · Adventure · Change",
    6: "Harmony · Responsibility · Love",
    7: "Intuition · Wisdom · Mysticism",
    8: "Abundance · Authority · Manifestation",
    9: "Completion · Compassion · Universal Love",
  };

  return (
    <section id="gematria" className="py-20 px-6 bg-background border-t border-border">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-10">
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20 mx-auto mb-4">
            <Hash className="w-6 h-6 text-primary" />
          </div>
          <h2 className="font-serif text-3xl lg:text-4xl text-foreground mb-3">Chaldean Gematria</h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Every letter carries a vibration. The ancient Babylonian system assigns numbers 1–8 to each letter — try your name, a city, or any word below.
          </p>
        </div>

        <div className="glass-card rounded-2xl p-6 lg:p-8">
          <div className="flex gap-3 mb-6">
            <Input
              value={input}
              onChange={e => analyse(e.target.value)}
              placeholder="Type any name or word…"
              className="bg-background border-border rounded-xl h-12 text-lg"
              maxLength={40}
            />
            <Button
              onClick={() => analyse(input)}
              className="glow-button bg-primary text-primary-foreground h-12 rounded-xl shrink-0"
            >
              Analyse
            </Button>
          </div>

          {result && (
            <>
              {/* Letter breakdown */}
              <div className="flex flex-wrap gap-2 mb-6">
                {result.letters.map((l, i) => (
                  <div key={i} className="flex flex-col items-center bg-primary/5 border border-primary/10 rounded-lg px-3 py-2 min-w-[2.5rem]">
                    <span className="font-serif text-primary font-semibold text-lg leading-none">{l.letter}</span>
                    <span className="text-xs text-muted-foreground mt-1">{l.value}</span>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="flex-1 bg-primary/10 border border-primary/20 rounded-xl p-4 text-center">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Total</p>
                  <p className="font-serif text-3xl text-primary font-bold">{result.total}</p>
                </div>
                <div className="flex-1 bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 text-center">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Reduced</p>
                  <p className="font-serif text-3xl text-yellow-400 font-bold">{result.reduced}</p>
                </div>
                <div className="flex-1 bg-muted/40 border border-border rounded-xl p-4 text-center flex items-center justify-center">
                  <p className="text-sm text-muted-foreground leading-snug italic">
                    {NUMBER_THEMES[result.reduced] || "A sacred vibration"}
                  </p>
                </div>
              </div>

              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-3">Get your full natal chart with gematria, numerology, and AI guidance</p>
                <Button onClick={() => navigate("/auth?mode=register")} className="glow-button bg-primary text-primary-foreground rounded-xl">
                  <Sparkles className="w-4 h-4 mr-2" /> Create Your Free Chart
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
};

const NewsletterSection = () => {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/subscribe`, { email, name });
      setDone(true);
    } catch {
      // Even on duplicate, show success to avoid enumeration
      setDone(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="newsletter" className="py-20 px-6 bg-primary/5 border-t border-border">
      <div className="max-w-2xl mx-auto text-center">
        <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20 mx-auto mb-6">
          <Mail className="w-6 h-6 text-primary" />
        </div>
        <h2 className="font-serif text-3xl text-foreground mb-3">Stay Aligned</h2>
        <p className="text-muted-foreground mb-8">
          Weekly astrological insights, feature announcements, and cosmic guidance — straight to your inbox.
        </p>
        {done ? (
          <div className="flex items-center justify-center gap-3 text-green-500">
            <Check className="w-5 h-5" />
            <span className="font-medium">You're on the list! ✨</span>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <Input
              type="text"
              placeholder="Your name (optional)"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="bg-background border-border rounded-xl h-12"
            />
            <Input
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-background border-border rounded-xl h-12 flex-1"
              required
            />
            <Button type="submit" disabled={loading} className="glow-button bg-primary text-primary-foreground h-12 rounded-xl shrink-0">
              {loading ? <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" /> : <><Send className="w-4 h-4 mr-2" />Subscribe</>}
            </Button>
          </form>
        )}
      </div>
    </section>
  );
};

const ContactSection = () => {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/contact`, form);
      setDone(true);
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to send message. Please try again.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="contact" className="py-24 px-6">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-primary font-semibold mb-3 tracking-widest text-sm uppercase">Contact</p>
          <h2 className="font-serif text-foreground">Get in Touch</h2>
          <p className="text-muted-foreground mt-3">Questions, partnerships, or feedback — we'd love to hear from you.</p>
        </div>

        {done ? (
          <div className="glass-card rounded-2xl p-10 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mx-auto">
              <Check className="w-8 h-8 text-green-500" />
            </div>
            <h3 className="font-serif text-2xl text-foreground">Message Received ✨</h3>
            <p className="text-muted-foreground">We'll get back to you within 1–2 business days. Check your inbox for a confirmation.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-8 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-foreground">Name</label>
                <Input name="name" placeholder="Your name" value={form.name} onChange={handleChange}
                  className="bg-muted/30 border-border rounded-xl" required />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-foreground">Email</label>
                <Input name="email" type="email" placeholder="your@email.com" value={form.email} onChange={handleChange}
                  className="bg-muted/30 border-border rounded-xl" required />
              </div>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground">Subject</label>
              <Input name="subject" placeholder="What's on your mind?" value={form.subject} onChange={handleChange}
                className="bg-muted/30 border-border rounded-xl" required />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground">Message</label>
              <Textarea name="message" placeholder="Tell us more..." value={form.message} onChange={handleChange}
                className="bg-muted/30 border-border rounded-xl min-h-[140px]" required />
            </div>
            <Button type="submit" disabled={loading} className="w-full glow-button bg-primary text-primary-foreground h-12 rounded-xl">
              {loading
                ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />Sending...</span>
                : <><Send className="w-4 h-4 mr-2" />Send Message</>}
            </Button>
          </form>
        )}
      </div>
    </section>
  );
};

const Footer = () => {
  return (
    <footer className="border-t border-border py-12 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-primary" />
            </div>
            <span className="font-serif text-lg text-foreground">Gab44</span>
          </div>
          
          <p className="text-sm text-muted-foreground">
            © 2026 Gab44. Helping humanity align with truth.
          </p>

          <div className="flex gap-6">
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Privacy</a>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Terms</a>
            <a href="#contact" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <HeroSection />
      <GematriaSection />
      <FeaturesSection />
      <ChatPreview />
      <TestimonialsSection />
      <PricingSection />
      <FAQSection />
      <CTASection />
      <NewsletterSection />
      <ContactSection />
      <Footer />
    </div>
  );
}
