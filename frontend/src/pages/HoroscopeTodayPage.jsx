import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { Sparkles, ArrowLeft, ArrowRight, Star } from "lucide-react";
import BuyReadingButton from "@/components/BuyReadingButton";
import ReadingTrustStrip from "@/components/ReadingTrustStrip";

const SIGN_GLYPHS = {
  aries: "♈", taurus: "♉", gemini: "♊", cancer: "♋",
  leo: "♌", virgo: "♍", libra: "♎", scorpio: "♏",
  sagittarius: "♐", capricorn: "♑", aquarius: "♒", pisces: "♓",
};

function todayHuman() {
  return new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

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

export default function HoroscopeTodayPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    axios
      .get(`${API}/horoscope/daily`)
      .then((res) => {
        if (!cancelled) setData(res.data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err?.response?.data?.detail || "Could not load today's horoscopes.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const url = "https://gab44.com/horoscope/today";
    const title = `Today's Horoscope for All 12 Zodiac Signs (${todayHuman()}) — Gab44`;
    const description =
      "Daily horoscopes for all 12 zodiac signs — Aries through Pisces. Love, career, wellness, and lucky number for today, refreshed every morning by Gab44.";
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
    return () => {
      document.title = prevTitle;
    };
  }, []);

  return (
    <div className="min-h-screen bg-background cosmic-page-bg">
      {/* Slim top bar */}
      <header className="border-b border-border/50 backdrop-blur-md bg-background/70 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">Gab44 home</span>
          </Link>
          <Link to="/auth?mode=register" className="text-sm text-primary hover:underline">
            Create free chart →
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="px-4 sm:px-6 pt-10 pb-10">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 mb-6">
            <Sparkles className="w-3.5 h-3.5 text-primary" />
            <span className="text-[11px] sm:text-xs font-semibold text-primary tracking-wide uppercase">
              All 12 signs · {todayHuman()}
            </span>
          </div>
          <h1 className="font-serif text-foreground text-3xl sm:text-4xl md:text-5xl mb-4">
            Today's Horoscope
          </h1>
          <p className="text-muted-foreground text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
            One quick read of the cosmic weather for every sign. Tap any card
            for the full daily breakdown, audio reading, and lucky details.
          </p>
        </div>
      </section>

      {/* Sign grid */}
      <section className="px-4 sm:px-6 pb-12">
        <div className="max-w-5xl mx-auto">
          {loading && (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="glass-card rounded-2xl p-5 animate-pulse">
                  <div className="h-6 bg-muted/40 rounded w-1/3 mb-4" />
                  <div className="h-4 bg-muted/30 rounded w-full mb-2" />
                  <div className="h-4 bg-muted/30 rounded w-5/6" />
                </div>
              ))}
            </div>
          )}

          {error && !loading && (
            <p className="text-center text-muted-foreground">{error}</p>
          )}

          {!loading && !error && data && (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.signs.map((s) => (
                <Link
                  key={s.slug}
                  to={`/zodiac/${s.slug}`}
                  className="glass-card rounded-2xl p-5 hover:border-primary/40 transition-colors flex flex-col"
                  data-testid={`horoscope-today-card-${s.slug}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl select-none" aria-hidden>
                        {SIGN_GLYPHS[s.slug]}
                      </span>
                      <div>
                        <p className="font-serif text-lg text-foreground capitalize">
                          {s.sign}
                        </p>
                        <p className="text-[11px] text-muted-foreground/70">
                          {s.date_range}
                        </p>
                      </div>
                    </div>
                    {s.lucky_number != null && (
                      <span className="text-xs font-mono px-2 py-1 rounded-md bg-primary/10 text-primary border border-primary/20">
                        #{s.lucky_number}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-foreground/90 leading-relaxed line-clamp-4 flex-1">
                    {s.summary}
                  </p>
                  <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
                    {s.mood ? (
                      <span className="capitalize">Mood · {s.mood}</span>
                    ) : (
                      <span />
                    )}
                    <span className="text-primary inline-flex items-center gap-1">
                      Read full <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Trust + CTA */}
      <section className="px-4 sm:px-6 pb-16">
        <div className="max-w-3xl mx-auto glass-card rounded-2xl p-6 md:p-8 text-center">
          <h2 className="font-serif text-2xl md:text-3xl text-foreground mb-3">
            Sun signs are the headline. Your chart is the story.
          </h2>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            Today's horoscope only sees your sun sign. A full personalized
            reading factors in your moon, rising, planetary placements, and
            the live transits affecting your chart right now.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/auth?mode=register">
              <button
                className="rounded-xl glow-button bg-primary text-primary-foreground px-6 py-4 text-base inline-flex items-center gap-2 w-full sm:w-auto justify-center"
                data-testid="horoscope-today-cta-signup"
              >
                <Star className="w-4 h-4" />
                Create free chart
              </button>
            </Link>
            <BuyReadingButton
              label="Personal reading — $19"
              testId="horoscope-today-cta-buy"
              className="px-6 py-4 text-base"
              variant="secondary"
            />
          </div>
          <ReadingTrustStrip className="mt-5" />
        </div>
      </section>
    </div>
  );
}
