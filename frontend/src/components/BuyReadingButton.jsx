import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Loader2, Sparkles } from "lucide-react";
import { useAuth, API } from "@/App";
import { Button } from "@/components/ui/button";

/**
 * One-click checkout for the $19 Personal Astrology Reading.
 * Works for both authed and guest users — for guests Stripe collects the
 * email on the hosted Checkout page.
 */
export default function BuyReadingButton({
  className = "",
  label = "Buy Reading — $19",
  variant = "primary",
  size = "default",
  payload = {},
  testId = "buy-reading-btn",
}) {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.post(
        `${API}/payments/buy-reading`,
        payload || {},
        { headers }
      );
      if (res.data?.checkout_url) {
        window.location.href = res.data.checkout_url;
        return;
      }
      toast.error("Could not start checkout. Please try again.");
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        "Something went wrong starting checkout. No charge was made — try again in a moment.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const baseClasses =
    variant === "primary"
      ? "glow-button bg-primary text-primary-foreground"
      : "bg-secondary text-secondary-foreground";

  return (
    <Button
      onClick={handleClick}
      disabled={loading}
      className={`rounded-xl ${baseClasses} ${className}`}
      size={size}
      data-testid={testId}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin" />
          Redirecting…
        </span>
      ) : (
        <span className="flex items-center gap-2">
          <Sparkles className="w-4 h-4" />
          {label}
        </span>
      )}
    </Button>
  );
}
