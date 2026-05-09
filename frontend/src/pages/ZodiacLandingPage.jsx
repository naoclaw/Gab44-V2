import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams, Navigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { Button } from "@/components/ui/button";
import BuyReadingButton from "@/components/BuyReadingButton";
import ReadingTrustStrip from "@/components/ReadingTrustStrip";
import {
  Sparkles,
  Heart,
  Briefcase,
  Leaf,
  Star,
  ArrowRight,
  Sun,
  Moon,
  ArrowLeft,
  Play,
  Pause,
  Volume2,
} from "lucide-react";

const ZODIAC = {
  aries:       { name: "Aries",       glyph: "♈", element: "Fire",  ruler: "Mars",     dates: "March 21 – April 19",       traits: ["Natural leader, fearless trailblazer", "Driven by passion and independence", "Thrives on challenge and new beginnings"] },
  taurus:      { name: "Taurus",      glyph: "♉", element: "Earth", ruler: "Venus",    dates: "April 20 – May 20",          traits: ["Grounded builder, sensory connoisseur", "Values stability, loyalty, and beauty", "Patient determination that moves mountains"] },
  gemini:      { name: "Gemini",      glyph: "♊", element: "Air",   ruler: "Mercury",  dates: "May 21 – June 20",           traits: ["Quick-witted communicator, eternal student", "Thrives on variety and intellectual connection", "Adaptable mind that bridges worlds"] },
  cancer:      { name: "Cancer",      glyph: "♋", element: "Water", ruler: "Moon",     dates: "June 21 – July 22",          traits: ["Intuitive nurturer, emotional depth", "Fierce protector of loved ones", "Deep connection to home and heritage"] },
  leo:         { name: "Leo",         glyph: "♌", element: "Fire",  ruler: "Sun",      dates: "July 23 – August 22",        traits: ["Radiant creator, natural performer", "Generous heart with magnetic presence", "Born to inspire and lead with warmth"] },
  virgo:       { name: "Virgo",       glyph: "♍", element: "Earth", ruler: "Mercury",  dates: "August 23 – September 22",   traits: ["Precise analyst, devoted healer", "Eye for detail that others miss", "Service-oriented with quiet strength"] },
  libra:       { name: "Libra",       glyph: "♎", element: "Air",   ruler: "Venus",    dates: "September 23 – October 22",  traits: ["Diplomatic peacemaker, aesthetic visionary", "Seeks balance in all relationships", "Natural mediator who sees every perspective"] },
  scorpio:     { name: "Scorpio",     glyph: "♏", element: "Water", ruler: "Pluto",    dates: "October 23 – November 21",   traits: ["Intense transformer, truth-seeker", "Penetrating insight into the hidden", "Power through vulnerability and depth"] },
  sagittarius: { name: "Sagittarius", glyph: "♐", element: "Fire",  ruler: "Jupiter",  dates: "November 22 – December 21",  traits: ["Optimistic philosopher, born explorer", "Seeks meaning in every experience", "Freedom-loving with an infectious enthusiasm"] },
  capricorn:   { name: "Capricorn",   glyph: "♑", element: "Earth", ruler: "Saturn",   dates: "December 22 – January 19",   traits: ["Ambitious architect, strategic thinker", "Builds empires through discipline", "Earns legacy through patience and persistence"] },
  aquarius:    { name: "Aquarius",    glyph: "♒", element: "Air",   ruler: "Uranus",   dates: "January 20 – February 18",   traits: ["Visionary humanitarian, original thinker", "Champions the collective over the individual", "Ahead of their time in thought and action"] },
  pisces:      { name: "Pisces",      glyph: "♓", element: "Water", ruler: "Neptune",  dates: "February 19 – March 20",     traits: ["Empathic dreamer, spiritual sponge", "Sees the world through compassion", "Creative depth that transcends the ordinary"] },
};

const SLUGS = Object.keys(ZODIAC);

function setMeta(name, content, attr = "name") {
  if (!content) return;
  let el = document.head.querySelector(`meta[${attr}="${name}"]`);
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attr, name);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function setCanonical(href) {
  let link = document.head.querySelector('link[rel="canonical"]');
  if (!link) {
    link = document.createElement("link");
    link.setAttribute("rel", "canonical");
    document.head.appendChild(link);
  }
  link.setAttribute("href", href);
}

function setJsonLd(id, data) {
  let script = document.head.querySelector(`script[data-jsonld="${id}"]`);
  if (!script) {
    script = document.createElement("script");
    script.setAttribute("type", "application/ld+json");
    script.setAttribute("data-jsonld", id);
    document.head.appendChild(script);
  }
  script.text = JSON.stringify(data);
}

function todayHuman() {
  return new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function VoicePreview({ slug, signName, disabled }) {
  const [state, setState] = useState("idle"); // idle | loading | playing | paused | error
  const [errorMsg, setErrorMsg] = useState("");
  const audioRef = useRef(null);
  const urlRef = useRef(null);

  useEffect(() => {
    return () => {
      if (urlRef.current) {
        URL.revokeObjectURL(urlRef.current);
        urlRef.current = null;
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // If the slug changes (e.g. via cross-sign nav), drop any cached audio.
  useEffect(() => {
    setState("idle");
    setErrorMsg("");
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current);
      urlRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  }, [slug]);

  const onClick = async () => {
    if (state === "playing" && audioRef.current) {
      audioRef.current.pause();
      setState("paused");
      return;
    }
    if (state === "paused" && audioRef.current) {
      audioRef.current.play();
      setState("playing");
      return;
    }
    setState("loading");
    setErrorMsg("");
    try {
      const res = await axios.get(`${API}/horoscope/daily/${slug}/voice`, {
        responseType: "blob",
      });
      const url = URL.createObjectURL(res.data);
      urlRef.current = url;
      const audio = new Audio(url);
      audio.onended = () => setState("idle");
      audio.onerror = () => {
        setErrorMsg("Playback failed.");
        setState("error");
      };
      audioRef.current = audio;
      await audio.play();
      setState("playing");
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setErrorMsg(
        typeof detail === "string"
          ? detail
          : "Voice preview unavailable right now."
      );
      setState("error");
    }
  };

  const isBusy = state === "loading";
  const Icon = state === "playing" ? Pause : state === "loading" ? Volume2 : Play;
  const label =
    state === "playing"
      ? "Pause preview"
      : state === "loading"
      ? "Loading…"
      : state === "paused"
      ? "Resume"
      : `Hear today's ${signName} reading`;

  return (
    <div
      className="mt-6 rounded-2xl border border-primary/20 bg-primary/5 p-4 md:p-5 flex flex-col sm:flex-row sm:items-center gap-4"
      data-testid="zodiac-voice-preview"
    >
      <button
        type="button"
        onClick={onClick}
        disabled={disabled || isBusy}
        className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary text-primary-foreground px-5 py-3 font-medium disabled:opacity-60 disabled:cursor-not-allowed hover:opacity-90 transition-opacity flex-shrink-0"
        data-testid="zodiac-voice-play"
        aria-label={label}
      >
        <Icon className={`w-4 h-4 ${isBusy ? "animate-pulse" : ""}`} />
        <span className="text-sm">{label}</span>
      </button>
      <div className="text-xs text-muted-foreground leading-relaxed">
        {state === "error" && errorMsg ? (
          <span className="text-destructive">{errorMsg}</span>
        ) : (
          <>
            Free 25-second narrated preview. Want a full reading shaped by{" "}
            <span className="text-foreground">your</span> birth chart and live
            transits?{" "}
            <Link to="/pricing" className="text-primary hover:underline">
              See plans →
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default function ZodiacLandingPage() {
  const { sign: slugParam } = useParams();
  const slug = (slugParam || "").toLowerCase();
  const meta = ZODIAC[slug];

  const [horoscope, setHoroscope] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!meta) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    axios
      .get(`${API}/horoscope/daily/${slug}`)
      .then((res) => {
        if (!cancelled) setHoroscope(res.data);
      })
      .catch((err) => {
        if (!cancelled) setError(err?.response?.data?.detail || "Could not load today's reading.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [slug, meta]);

  // Per-page SEO meta — set once when the sign changes, restore on unmount
  useEffect(() => {
    if (!meta) return;
    const url = `https://gab44.com/zodiac/${slug}`;
    const title = `${meta.name} Daily Horoscope (${todayHuman()}) — Gab44`;
    const description = `Today's ${meta.name} horoscope: love, career, wellness, lucky number and color. Free daily reading powered by AI astrologers — refreshed every morning.`;

    const prevTitle = document.title;
    document.title = title;

    setMeta("description", description);
    setMeta("og:title", title, "property");
    setMeta("og:description", description, "property");
    setMeta("og:type", "article", "property");
    setMeta("og:url", url, "property");
    setMeta("twitter:title", title);
    setMeta("twitter:description", description);
    setCanonical(url);

    setJsonLd("zodiac-page", {
      "@context": "https://schema.org",
      "@type": "Article",
      headline: title,
      description,
      datePublished: new Date().toISOString().slice(0, 10),
      dateModified: new Date().toISOString().slice(0, 10),
      author: { "@type": "Organization", name: "Gab44" },
      publisher: {
        "@type": "Organization",
        name: "Gab44",
        logo: { "@type": "ImageObject", url: "https://gab44.com/favicon.svg" },
      },
      mainEntityOfPage: url,
      about: { "@type": "Thing", name: `${meta.name} zodiac sign` },
    });

    return () => {
      document.title = prevTitle;
      const ld = document.head.querySelector('script[data-jsonld="zodiac-page"]');
      if (ld) ld.remove();
    };
  }, [slug, meta]);

  const otherSigns = useMemo(
    () => SLUGS.filter((s) => s !== slug).map((s) => ({ slug: s, ...ZODIAC[s] })),
    [slug]
  );

  if (!meta) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-background cosmic-page-bg">
      {/* Slim top bar */}
      <header className="border-b border-border/50 backdrop-blur-md bg-background/70 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">Gab44 home</span>
          </Link>
          <Link to="/auth?mode=register" className="text-sm text-primary hover:underline" data-testid="zodiac-nav-signup">
            Create free chart →
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="px-4 sm:px-6 pt-10 sm:pt-12 pb-12 sm:pb-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 mb-6">
            <Sparkles className="w-3.5 h-3.5 text-primary" />
            <span className="text-[11px] sm:text-xs font-semibold text-primary tracking-wide uppercase">
              Daily Horoscope · {todayHuman()}
            </span>
          </div>

          <div className="text-6xl sm:text-7xl mb-4 select-none" aria-hidden>
            {meta.glyph}
          </div>
          <h1 className="font-serif text-foreground text-3xl sm:text-4xl md:text-5xl mb-4">
            {meta.name} Horoscope
          </h1>
          <p className="text-muted-foreground text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
            {meta.dates} · {meta.element} sign · ruled by {meta.ruler}.
          </p>

          {/* Today's headline */}
          <div className="glass-card rounded-2xl p-6 md:p-8 mt-10 text-left" data-testid="zodiac-summary">
            {loading ? (
              <div className="space-y-3 animate-pulse">
                <div className="h-4 bg-muted/50 rounded w-3/4" />
                <div className="h-4 bg-muted/50 rounded w-full" />
                <div className="h-4 bg-muted/50 rounded w-5/6" />
              </div>
            ) : error ? (
              <p className="text-muted-foreground">{error}</p>
            ) : (
              <>
                <p className="text-xs font-semibold uppercase tracking-wider text-primary/80 mb-3">
                  Today's energy
                </p>
                <p className="font-serif text-xl md:text-2xl text-foreground leading-relaxed">
                  {horoscope?.summary}
                </p>
                {horoscope && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-6 text-sm">
                    <div className="rounded-xl bg-muted/30 px-3 py-2">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground/70">Mood</p>
                      <p className="capitalize text-foreground font-medium">{horoscope.mood}</p>
                    </div>
                    <div className="rounded-xl bg-muted/30 px-3 py-2">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground/70">Lucky color</p>
                      <p className="capitalize text-foreground font-medium">{horoscope.lucky_color}</p>
                    </div>
                    <div className="rounded-xl bg-muted/30 px-3 py-2 col-span-2 md:col-span-1">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground/70">Lucky number</p>
                      <p className="text-foreground font-medium">{horoscope.lucky_number}</p>
                    </div>
                  </div>
                )}
                <VoicePreview
                  slug={slug}
                  signName={meta.name}
                  disabled={!horoscope}
                />
              </>
            )}
          </div>

          {/* Primary CTAs */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link to="/auth?mode=register">
              <Button
                size="lg"
                className="rounded-xl glow-button bg-primary text-primary-foreground gap-2 px-8 py-6 text-base"
                data-testid="zodiac-cta-signup"
              >
                <Sparkles className="w-4 h-4" />
                Create your free chart
              </Button>
            </Link>
            <BuyReadingButton
              label={`${meta.name} personal reading — $19`}
              testId="zodiac-cta-buy"
              className="px-6 py-6 text-base"
              variant="secondary"
            />
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            Free chart · no credit card · or skip the wait with a written reading
          </p>
          <ReadingTrustStrip className="mt-3" />
        </div>
      </section>

      {/* Three-column daily breakdown */}
      <section className="px-6 pb-16">
        <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-4">
          <DailyCard
            icon={Heart}
            tone="text-pink-500"
            label="Love"
            body={loading ? null : horoscope?.love}
          />
          <DailyCard
            icon={Briefcase}
            tone="text-amber-500"
            label="Career"
            body={loading ? null : horoscope?.career}
          />
          <DailyCard
            icon={Leaf}
            tone="text-emerald-500"
            label="Wellness"
            body={loading ? null : horoscope?.wellness}
          />
        </div>
      </section>

      {/* Traits / about */}
      <section className="px-6 pb-16">
        <div className="max-w-4xl mx-auto glass-card rounded-2xl p-6 md:p-8">
          <h2 className="font-serif text-2xl md:text-3xl text-foreground mb-4">
            About {meta.name}
          </h2>
          <p className="text-muted-foreground leading-relaxed mb-6">
            {meta.name} is a{" "}
            <span className="text-foreground">{meta.element}</span> sign ruled by{" "}
            <span className="text-foreground">{meta.ruler}</span>, born between{" "}
            <span className="text-foreground">{meta.dates}</span>. The
            archetype runs deep — but every {meta.name} carries its own unique
            constellation of moon, rising, and planetary placements that shape
            who they actually are.
          </p>
          <ul className="space-y-3 mb-6">
            {meta.traits.map((trait, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-foreground/90">
                <Star className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                {trait}
              </li>
            ))}
          </ul>
          <div className="rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm text-muted-foreground">
            Want the full picture? Your sun sign is just the headline —
            calculate your free birth chart to see where the moon, Mercury,
            Venus, and the rising sign land in your unique map of the sky.
          </div>
        </div>
      </section>

      {/* Cross-sign nav */}
      <section className="px-6 pb-16">
        <div className="max-w-5xl mx-auto">
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60 mb-4">
            Other zodiac signs
          </p>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
            {otherSigns.map((s) => (
              <Link
                key={s.slug}
                to={`/zodiac/${s.slug}`}
                className="glass-card rounded-xl px-3 py-3 text-center hover:border-primary/30 transition-colors"
                data-testid={`zodiac-link-${s.slug}`}
              >
                <div className="text-2xl mb-1" aria-hidden>{s.glyph}</div>
                <p className="text-sm text-foreground">{s.name}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="px-6 pb-20">
        <div className="max-w-3xl mx-auto glass-card rounded-2xl p-8 text-center">
          <h2 className="font-serif text-2xl md:text-3xl text-foreground mb-3">
            Your sign is the start, not the story
          </h2>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            Get a fully personalized written reading drawn from your full natal chart.
            Delivered within 48 hours. No subscription.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <BuyReadingButton
              label="Buy personal reading — $19"
              testId="zodiac-cta-buy-bottom"
              className="px-6 py-6 text-base"
            />
            <Link to="/pricing">
              <Button variant="outline" size="lg" className="rounded-xl gap-2 px-6 py-6 text-base">
                See all plans <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
          <ReadingTrustStrip className="mt-5" />
        </div>
      </section>

      {/* Slim footer */}
      <footer className="border-t border-border py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-muted-foreground">
          <p>© 2026 Gab44 · Daily {meta.name} horoscope refreshed every morning.</p>
          <div className="flex items-center gap-4">
            <Link to="/" className="hover:text-foreground">Home</Link>
            <Link to="/pricing" className="hover:text-foreground">Pricing</Link>
            <a href="mailto:contact@gab44.com" className="hover:text-foreground">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function DailyCard({ icon: Icon, tone, label, body }) {
  return (
    <div className="glass-card rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <Icon className={`w-4 h-4 ${tone}`} />
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/80">
          {label}
        </p>
      </div>
      {body == null ? (
        <div className="space-y-2 animate-pulse">
          <div className="h-3 bg-muted/50 rounded w-full" />
          <div className="h-3 bg-muted/50 rounded w-5/6" />
        </div>
      ) : (
        <p className="text-sm text-foreground/90 leading-relaxed">{body}</p>
      )}
    </div>
  );
}

export const ZODIAC_SLUGS = SLUGS;
