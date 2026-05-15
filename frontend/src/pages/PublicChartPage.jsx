import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { Sparkles, Loader2, XCircle, Download } from "lucide-react";
import { Button } from "@/components/ui/button";

function setMeta(name, content, attr = "name") {
  if (!content) return null;
  let el = document.head.querySelector(`meta[${attr}="${name}"]`);
  let created = false;
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attr, name);
    created = true;
    document.head.appendChild(el);
  }
  const prev = el.getAttribute("content");
  el.setAttribute("content", content);
  return { el, prev, created };
}

function setLink(rel, href) {
  if (!href) return null;
  let el = document.head.querySelector(`link[rel="${rel}"]`);
  let created = false;
  if (!el) {
    el = document.createElement("link");
    el.setAttribute("rel", rel);
    created = true;
    document.head.appendChild(el);
  }
  const prev = el.getAttribute("href");
  el.setAttribute("href", href);
  return { el, prev, created };
}

const SIGN_SYMBOLS = {
  Aries: "♈", Taurus: "♉", Gemini: "♊", Cancer: "♋", Leo: "♌", Virgo: "♍",
  Libra: "♎", Scorpio: "♏", Sagittarius: "♐", Capricorn: "♑", Aquarius: "♒", Pisces: "♓"
};
const SIGN_COLORS = {
  Aries: "#FF6B6B", Taurus: "#4ECDC4", Gemini: "#FFE66D", Cancer: "#C9CCD5",
  Leo: "#FF9F43", Virgo: "#A3CB38", Libra: "#FDA7DF", Scorpio: "#9B59B6",
  Sagittarius: "#E74C3C", Capricorn: "#5D6D7E", Aquarius: "#3498DB", Pisces: "#1ABC9C"
};
const getElement = (sign) => ({ Aries:"Fire",Leo:"Fire",Sagittarius:"Fire",Taurus:"Earth",Virgo:"Earth",Capricorn:"Earth",Gemini:"Air",Libra:"Air",Aquarius:"Air",Cancer:"Water",Scorpio:"Water",Pisces:"Water" }[sign] || "");

export default function PublicChartPage() {
  const { token } = useParams();
  const [chart, setChart] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    axios.get(`${API}/chart/public/${token}`)
      .then(r => { setChart(r.data); setStatus("ok"); })
      .catch(() => setStatus("error"));
  }, [token]);

  // Per-page social-share meta. Only fires once the chart has loaded so
  // we have the buyer's first name and sun sign to make the preview pop.
  useEffect(() => {
    if (status !== "ok" || !chart) return;
    const firstName = (chart.name || "").toString().split(" ")[0] || "Their";
    const possessive = firstName.endsWith("s") ? `${firstName}'` : `${firstName}'s`;
    const sunSign = chart.sun_sign || "";
    const title = sunSign
      ? `${possessive} cosmic blueprint — ${sunSign} · Gab44`
      : `${possessive} cosmic blueprint · Gab44`;
    const description = sunSign
      ? `A ${sunSign} sun, with moon and rising mapped to astronomical precision. Discover your own chart at gab44.com.`
      : "A natal chart mapped to astronomical precision. Discover your own at gab44.com.";
    const url = `https://gab44.com/chart/public/${token}`;
    const imageUrl = `${API}/chart/public/${token}/image.png?style=card&size=1080`;

    const prevTitle = document.title;
    document.title = title;

    const restorers = [
      setMeta("description", description),
      setMeta("og:title", title, "property"),
      setMeta("og:description", description, "property"),
      setMeta("og:type", "article", "property"),
      setMeta("og:url", url, "property"),
      setMeta("og:image", imageUrl, "property"),
      setMeta("og:image:width", "1080", "property"),
      setMeta("og:image:height", "1080", "property"),
      setMeta("twitter:card", "summary_large_image"),
      setMeta("twitter:title", title),
      setMeta("twitter:description", description),
      setMeta("twitter:image", imageUrl),
      setLink("canonical", url),
    ].filter(Boolean);

    return () => {
      document.title = prevTitle;
      for (const r of restorers) {
        if (!r) continue;
        if (r.created) {
          r.el.remove();
        } else if (r.prev != null) {
          if (r.el.tagName === "META") r.el.setAttribute("content", r.prev);
          else r.el.setAttribute("href", r.prev);
        }
      }
    };
  }, [status, chart, token]);

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-background cosmic-page-bg flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="min-h-screen bg-background cosmic-page-bg flex items-center justify-center p-8">
        <div className="glass-card rounded-2xl p-10 max-w-sm w-full text-center space-y-4">
          <XCircle className="w-12 h-12 text-destructive mx-auto" />
          <h1 className="font-serif text-2xl text-foreground">Chart Not Found</h1>
          <p className="text-muted-foreground">This chart may have been made private or the link is invalid.</p>
          <Link to="/"><Button className="w-full rounded-xl">Discover your chart at Gab44</Button></Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background cosmic-page-bg py-12 px-4">
      {/* Header */}
      <div className="max-w-xl mx-auto mb-8 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
            <Sparkles className="w-4 h-4 text-primary" />
          </div>
          <span className="font-serif text-lg text-foreground">Gab44</span>
        </Link>
        <Link to="/auth?mode=register">
          <Button variant="outline" size="sm" className="rounded-xl">Create My Chart</Button>
        </Link>
      </div>

      {/* Server-rendered share card image — high-fidelity PNG with full wheel */}
      <div className="max-w-xl mx-auto rounded-2xl overflow-hidden shadow-2xl mb-6 bg-[#0F0F14]">
        <img
          src={`${API}/chart/public/${token}/image.png?style=card&size=1080`}
          alt="Cosmic blueprint share card"
          className="block w-full h-auto"
          loading="lazy"
          data-testid="public-chart-image"
        />
      </div>

      <div className="max-w-xl mx-auto flex flex-wrap gap-3 justify-center mb-8">
        <a
          href={`${API}/chart/public/${token}/image.png?style=card&size=1080`}
          download="gab44-cosmic-blueprint.png"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500 text-black text-sm font-medium hover:bg-amber-600 transition-colors"
          data-testid="public-chart-download-card"
        >
          <Download className="w-4 h-4" />
          Download share card
        </a>
        <a
          href={`${API}/chart/public/${token}/image.png?style=wheel&size=1600`}
          download="gab44-natal-wheel.png"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-muted/40 text-foreground text-sm font-medium hover:bg-muted/60 transition-colors border border-border"
          data-testid="public-chart-download-wheel"
        >
          <Download className="w-4 h-4" />
          Download natal wheel
        </a>
      </div>

      {/* Detailed planet/pattern breakdown below the share image */}
      <div className="max-w-xl mx-auto rounded-2xl overflow-hidden shadow-2xl"
           style={{ background: "linear-gradient(135deg, #0F0F14 0%, #1a1a2e 50%, #16213e 100%)" }}>
        <div className="relative p-8">
          {/* Background symbols */}
          <div className="absolute inset-0 opacity-10 pointer-events-none">
            <div className="absolute top-10 left-10 text-6xl">✦</div>
            <div className="absolute top-20 right-20 text-4xl">✧</div>
            <div className="absolute bottom-20 left-20 text-5xl">✦</div>
            <div className="absolute bottom-10 right-10 text-3xl">✧</div>
          </div>

          <div className="relative text-center mb-8">
            <p className="text-amber-400/80 text-sm uppercase tracking-widest mb-1">Cosmic Blueprint</p>
            <p className="text-white/50 text-xs">{chart.birth_date} · {chart.birth_place}</p>
          </div>

          {/* Big Three */}
          <div className="relative w-64 h-64 mx-auto mb-8">
            <div className="absolute inset-0 rounded-full border-2 border-amber-400/30" />
            <div className="absolute inset-2 rounded-full border border-white/10" />

            {/* Sun */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
              <div className="w-20 h-20 rounded-full flex items-center justify-center text-3xl mb-1"
                   style={{ background: `linear-gradient(135deg, ${SIGN_COLORS[chart.sun_sign]}40, ${SIGN_COLORS[chart.sun_sign]}20)`, border: `2px solid ${SIGN_COLORS[chart.sun_sign]}60` }}>
                {SIGN_SYMBOLS[chart.sun_sign]}
              </div>
              <p className="text-white text-sm font-medium">{chart.sun_sign}</p>
              <p className="text-amber-400/60 text-xs">Sun</p>
            </div>

            {/* Moon */}
            <div className="absolute bottom-4 left-0 -translate-x-1/4 text-center">
              <div className="w-16 h-16 rounded-full flex items-center justify-center text-2xl mb-1"
                   style={{ background: `linear-gradient(135deg, ${SIGN_COLORS[chart.moon_sign]}40, ${SIGN_COLORS[chart.moon_sign]}20)`, border: `2px solid ${SIGN_COLORS[chart.moon_sign]}60` }}>
                {SIGN_SYMBOLS[chart.moon_sign]}
              </div>
              <p className="text-white text-xs font-medium">{chart.moon_sign}</p>
              <p className="text-gray-400 text-xs">Moon</p>
            </div>

            {/* Rising */}
            <div className="absolute bottom-4 right-0 translate-x-1/4 text-center">
              <div className="w-16 h-16 rounded-full flex items-center justify-center text-2xl mb-1"
                   style={{ background: `linear-gradient(135deg, ${SIGN_COLORS[chart.rising_sign]}40, ${SIGN_COLORS[chart.rising_sign]}20)`, border: `2px solid ${SIGN_COLORS[chart.rising_sign]}60` }}>
                {SIGN_SYMBOLS[chart.rising_sign]}
              </div>
              <p className="text-white text-xs font-medium">{chart.rising_sign}</p>
              <p className="text-gray-400 text-xs">Rising</p>
            </div>

            {/* Centre element */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className="text-white/60 text-xs mb-1">Element</p>
                <p className="text-amber-400 font-serif text-lg">{getElement(chart.sun_sign)}</p>
              </div>
            </div>
          </div>

          {/* Planets table */}
          {chart.planets && Object.keys(chart.planets).length > 0 && (
            <div className="grid grid-cols-2 gap-2 mb-6">
              {Object.entries(chart.planets).map(([planet, data]) => (
                <div key={planet} className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-2">
                  <span className="text-amber-400/80 text-sm w-20 truncate">{planet}</span>
                  <span className="text-white/80 text-sm">{SIGN_SYMBOLS[data.sign] || ""} {data.sign}</span>
                </div>
              ))}
            </div>
          )}

          {/* Patterns */}
          {chart.patterns?.length > 0 && (
            <div className="text-center mb-6">
              <p className="text-white/60 text-xs mb-2">Chart Patterns</p>
              <div className="flex flex-wrap justify-center gap-2">
                {chart.patterns.map((p, i) => (
                  <span key={i} className="bg-amber-400/10 border border-amber-400/20 rounded-full px-3 py-1 text-xs text-amber-400">{p}</span>
                ))}
              </div>
            </div>
          )}

          <div className="text-center pt-4 border-t border-white/10">
            <p className="text-white/40 text-xs">Discover your cosmic blueprint at</p>
            <p className="text-amber-400 font-medium">gab44.com</p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="max-w-xl mx-auto mt-8 text-center">
        <p className="text-muted-foreground mb-4">Curious about your own chart?</p>
        <Link to="/auth?mode=register">
          <Button className="glow-button bg-primary text-primary-foreground rounded-xl px-8">
            Get My Free Chart ✨
          </Button>
        </Link>
      </div>
    </div>
  );
}
