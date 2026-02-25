import { useState, useEffect } from "react";
import { useNavigate, Link, useSearchParams } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTheme } from "@/context/ThemeContext";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Sparkles, Check, ArrowLeft, Star, Sun, Moon } from "lucide-react";

export default function PricingPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, token } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(null);

  useEffect(() => {
    if (searchParams.get("upgrade") === "cancelled") {
      toast.info("Upgrade cancelled. You can upgrade anytime.");
    }
  }, [searchParams]);

  useEffect(() => {
    const fetchPricing = async () => {
      try {
        const response = await axios.get(`${API}/pricing`);
        setPlans(response.data.plans);
      } catch (error) {
        console.error("Error fetching pricing:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchPricing();
  }, []);

  const handleUpgrade = async (planId) => {
    if (!user) {
      navigate("/auth?mode=register");
      return;
    }
    if (planId === "seeker") {
      navigate("/dashboard");
      return;
    }
    if (user.subscription_tier === planId) {
      toast.info("You're already on this plan!");
      return;
    }

    setCheckoutLoading(planId);
    try {
      const res = await axios.post(
        `${API}/payments/checkout`,
        { tier: planId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Redirect to Stripe Checkout
      window.location.href = res.data.url;
    } catch (error) {
      const msg = error.response?.data?.detail || "Unable to start checkout";
      toast.error(msg);
      setCheckoutLoading(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-primary/20" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-8">
            <Link to="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back to Home</span>
            </Link>
            <button
              onClick={toggleTheme}
              className="w-10 h-10 rounded-xl bg-muted/50 hover:bg-muted flex items-center justify-center transition-colors border border-border/50"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <Sun className="w-5 h-5 text-primary" /> : <Moon className="w-5 h-5 text-muted-foreground" />}
            </button>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <span className="font-serif text-xl text-foreground">Gab44</span>
            </div>
            <h1 className="font-serif text-foreground mb-4">
              Choose Your Path
            </h1>
            <p className="text-muted-foreground max-w-xl mx-auto leading-relaxed">
              Flexible plans designed to meet you wherever you are on your journey. 
              Start free and upgrade when you're ready for deeper guidance.
            </p>
          </div>
        </div>

        {/* Pricing Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {plans.map((plan, index) => (
            <div 
              key={plan.id}
              className={`glass-card rounded-2xl p-6 relative card-lift ${plan.popular ? 'pricing-popular' : ''}`}
              data-testid={`pricing-plan-${index}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-xs font-semibold px-4 py-1.5 rounded-full flex items-center gap-1">
                  <Star className="w-3 h-3" />
                  Most Popular
                </div>
              )}
              
              <h3 className="font-serif text-xl text-foreground mb-1">{plan.name}</h3>
              <p className="text-sm text-muted-foreground mb-6">{plan.tagline}</p>
              
              <div className="mb-6">
                <span className="font-serif text-4xl text-foreground">${plan.price}</span>
                <span className="text-muted-foreground">/{plan.period}</span>
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
                onClick={() => handleUpgrade(plan.id)}
                disabled={checkoutLoading === plan.id || (user && user.subscription_tier === plan.id)}
                data-testid={`pricing-cta-${index}`}
              >
                {checkoutLoading === plan.id ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin" />
                    Redirecting...
                  </span>
                ) : user && user.subscription_tier === plan.id ? (
                  "Current Plan"
                ) : (
                  plan.cta
                )}
              </Button>
            </div>
          ))}
        </div>

        {/* FAQ Link */}
        <div className="text-center">
          <p className="text-muted-foreground">
            Have questions? Check our{" "}
            <Link to="/#faq" className="text-primary hover:underline">
              FAQ section
            </Link>{" "}
            or{" "}
            <a href="mailto:contact@gab44.com" className="text-primary hover:underline">
              contact us
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
