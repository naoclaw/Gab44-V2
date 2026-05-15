import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { API } from "@/App";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Sparkles,
  CheckCircle2,
  Mail,
  Clock,
  Loader2,
  ArrowRight,
  AlertCircle,
} from "lucide-react";

export default function ReadingThanksPage() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [savedOnce, setSavedOnce] = useState(false);

  const [form, setForm] = useState({
    name: "",
    birth_date: "",
    birth_time: "",
    birth_place: "",
    notes: "",
  });

  useEffect(() => {
    if (!sessionId) {
      setError("Missing checkout session id.");
      setLoading(false);
      return;
    }
    let cancelled = false;
    axios
      .get(`${API}/orders/reading/${sessionId}`)
      .then((res) => {
        if (cancelled) return;
        setOrder(res.data);
        setForm({
          name: res.data.name || "",
          birth_date: res.data.birth_date || "",
          birth_time: res.data.birth_time || "",
          birth_place: res.data.birth_place || "",
          notes: res.data.notes || "",
        });
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err?.response?.data?.detail || "Could not load your order.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  // SEO: this page should not be indexed
  useEffect(() => {
    const prevTitle = document.title;
    document.title = "Thank you — Gab44";
    let robots = document.head.querySelector('meta[name="robots"]');
    let created = false;
    if (!robots) {
      robots = document.createElement("meta");
      robots.setAttribute("name", "robots");
      created = true;
      document.head.appendChild(robots);
    }
    const prevContent = robots.getAttribute("content");
    robots.setAttribute("content", "noindex,nofollow");
    return () => {
      document.title = prevTitle;
      if (created) {
        robots.remove();
      } else if (prevContent != null) {
        robots.setAttribute("content", prevContent);
      }
    };
  }, []);

  const missingCount = useMemo(() => {
    if (!order) return 0;
    const fields = ["birth_date", "birth_time", "birth_place"];
    return fields.filter((k) => !order[k]).length;
  }, [order]);

  const setField = (key) => (e) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!sessionId) return;
    setSaving(true);
    try {
      const body = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [k, v?.trim?.() ?? v])
      );
      const res = await axios.patch(`${API}/orders/reading/${sessionId}/context`, body);
      setOrder(res.data);
      setSavedOnce(true);
      toast.success("Birth details saved — your astrologer has everything they need.");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Could not save your details. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background cosmic-page-bg flex items-center justify-center">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-primary/20" />
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-background cosmic-page-bg flex items-center justify-center px-6">
        <div className="glass-card rounded-2xl p-8 max-w-md text-center">
          <AlertCircle className="w-10 h-10 text-amber-500 mx-auto mb-4" />
          <h1 className="font-serif text-2xl text-foreground mb-2">We couldn't find your order</h1>
          <p className="text-muted-foreground text-sm mb-6">
            {error || "If you completed checkout, your reading is still safe — email us and we'll find it."}
          </p>
          <a href="mailto:contact@gab44.com">
            <Button className="rounded-xl bg-primary text-primary-foreground gap-2">
              <Mail className="w-4 h-4" />
              Email support
            </Button>
          </a>
        </div>
      </div>
    );
  }

  const isPaid = order.status === "paid" || order.status === "fulfilled";

  return (
    <div className="min-h-screen bg-background cosmic-page-bg">
      <header className="border-b border-border/50 backdrop-blur-md bg-background/70">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20">
              <Sparkles className="w-4 h-4 text-primary" />
            </div>
            <span className="font-serif text-lg text-foreground">Gab44</span>
          </Link>
          <Link to="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Home
          </Link>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-12">
        {/* Hero */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 mb-5">
            <CheckCircle2 className="w-8 h-8 text-green-500" />
          </div>
          <h1 className="font-serif text-3xl md:text-4xl text-foreground mb-3">
            {isPaid ? "Your reading is on the way" : "Thanks — almost there"}
          </h1>
          <p className="text-muted-foreground max-w-lg mx-auto">
            {isPaid
              ? "Payment received. Our astrologers will craft your personal reading and email it within 48 hours."
              : "Your order is being confirmed. You'll receive an email as soon as payment lands."}
          </p>
        </div>

        {/* Status pill */}
        <div className="glass-card rounded-2xl p-5 mb-6 flex items-center justify-between gap-3" data-testid="reading-thanks-status">
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-foreground">Delivery within 48 hours</p>
              <p className="text-xs text-muted-foreground">
                Sent to {order.email || "the email you used at checkout"}
              </p>
            </div>
          </div>
          <span
            className={`text-xs px-3 py-1 rounded-full border capitalize ${
              isPaid
                ? "bg-green-500/10 text-green-500 border-green-500/20"
                : "bg-amber-500/10 text-amber-500 border-amber-500/20"
            }`}
          >
            {order.status}
          </span>
        </div>

        {/* Context-completion form */}
        <div className="glass-card rounded-2xl p-6 md:p-8" data-testid="reading-thanks-form">
          <div className="mb-5">
            <h2 className="font-serif text-xl text-foreground mb-2">
              {missingCount > 0
                ? "Quick: share the missing birth details"
                : savedOnce
                ? "Got it — your astrologer has everything"
                : "Want to add or refine your birth details?"}
            </h2>
            <p className="text-sm text-muted-foreground">
              {missingCount > 0
                ? "Birth date, time and place are how astrologers calculate your full natal chart. The more accurate, the deeper the reading."
                : "Anything you change here will reach our astrologers before they start writing."}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="grid gap-4">
            <div className="grid gap-1.5">
              <Label htmlFor="thanks-name">Your name</Label>
              <Input
                id="thanks-name"
                value={form.name}
                onChange={setField("name")}
                placeholder="e.g. Alex Rivera"
                autoComplete="name"
                data-testid="thanks-name"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor="thanks-birth-date">Birth date</Label>
                <Input
                  id="thanks-birth-date"
                  type="date"
                  value={form.birth_date}
                  onChange={setField("birth_date")}
                  data-testid="thanks-birth-date"
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="thanks-birth-time">Birth time</Label>
                <Input
                  id="thanks-birth-time"
                  type="time"
                  value={form.birth_time}
                  onChange={setField("birth_time")}
                  data-testid="thanks-birth-time"
                />
              </div>
            </div>

            <div className="grid gap-1.5">
              <Label htmlFor="thanks-birth-place">Birth place</Label>
              <Input
                id="thanks-birth-place"
                value={form.birth_place}
                onChange={setField("birth_place")}
                placeholder="City, country"
                autoComplete="address-level2"
                data-testid="thanks-birth-place"
              />
            </div>

            <div className="grid gap-1.5">
              <Label htmlFor="thanks-notes">
                Anything specific you'd like the reading to focus on?
              </Label>
              <Textarea
                id="thanks-notes"
                value={form.notes}
                onChange={setField("notes")}
                placeholder="Career, a relationship, a decision you're weighing…"
                rows={3}
                maxLength={2000}
                data-testid="thanks-notes"
              />
            </div>

            <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-end mt-2">
              <Button
                type="submit"
                disabled={saving}
                className="rounded-xl glow-button bg-primary text-primary-foreground gap-2"
                data-testid="thanks-save-btn"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving…
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    {savedOnce ? "Update details" : "Send these details"}
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>

        {/* Next-step CTA */}
        <div className="mt-8 glass-card rounded-2xl p-6 text-center">
          <p className="text-muted-foreground mb-4">
            While you wait, explore your free birth chart on the dashboard.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/auth?mode=register">
              <Button variant="outline" className="rounded-xl gap-2">
                Create your free chart <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <a href="mailto:contact@gab44.com">
              <Button variant="ghost" className="rounded-xl gap-2">
                <Mail className="w-4 h-4" />
                Need help?
              </Button>
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}
