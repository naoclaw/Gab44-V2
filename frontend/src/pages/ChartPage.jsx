import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTheme } from "@/context/ThemeContext";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { 
  Sparkles, 
  ArrowLeft,
  Sun,
  Moon,
  Star,
  ChevronRight,
  Share2,
  Printer
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const PLANET_SYMBOLS = {
  sun: "☉", moon: "☽", mercury: "☿", venus: "♀", mars: "♂",
  jupiter: "♃", saturn: "♄", uranus: "♅", neptune: "♆", pluto: "♇",
  north_node: "☊", south_node: "☋", chiron: "⚷"
};

const SIGN_SYMBOLS = {
  Aries: "♈", Taurus: "♉", Gemini: "♊", Cancer: "♋", Leo: "♌", Virgo: "♍",
  Libra: "♎", Scorpio: "♏", Sagittarius: "♐", Capricorn: "♑", Aquarius: "♒", Pisces: "♓"
};

const getElement = (sign) => {
  const elements = {
    Aries: "Fire", Leo: "Fire", Sagittarius: "Fire",
    Taurus: "Earth", Virgo: "Earth", Capricorn: "Earth",
    Gemini: "Air", Libra: "Air", Aquarius: "Air",
    Cancer: "Water", Scorpio: "Water", Pisces: "Water"
  };
  return elements[sign] || "Unknown";
};

const ELEMENT_COLORS = {
  Fire: "text-orange-500", Earth: "text-green-500", Air: "text-cyan-500", Water: "text-blue-500"
};

export default function ChartPage() {
  const { user, token } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [chart, setChart] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchChart = async () => {
      try {
        const response = await axios.get(`${API}/chart/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setChart(response.data);
      } catch (error) {
        console.error("Error fetching chart:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchChart();
  }, [token]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-primary/40" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 print:hidden">
          <div>
            <div className="flex items-center gap-4 mb-4 print:hidden">
              <Link to="/dashboard" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm">Dashboard</span>
              </Link>
              <button
                onClick={toggleTheme}
                className="w-8 h-8 rounded-lg bg-muted/50 flex items-center justify-center"
                aria-label="Toggle theme"
              >
                {theme === "dark" ? <Sun className="w-4 h-4 text-primary" /> : <Moon className="w-4 h-4" />}
              </button>
            </div>
            <h1 className="font-serif text-3xl text-foreground">Your Birth Chart</h1>
            <p className="text-muted-foreground">
              Born {user?.birth_date} in {user?.birth_place}
            </p>
          </div>
          
          <div className="flex gap-3 print:hidden">
            <Button 
              onClick={() => window.print()}
              variant="outline"
              className="border-border rounded-xl"
              data-testid="print-chart-btn"
            >
              <Printer className="w-4 h-4 mr-2" />
              Print / PDF
            </Button>
            <Button 
              onClick={() => navigate("/share")}
              variant="outline"
              className="border-border rounded-xl"
              data-testid="share-chart-btn"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
            <Button 
              onClick={() => navigate("/chat")}
              className="bg-primary/10 text-primary hover:bg-primary/20 rounded-xl"
              data-testid="discuss-chart-btn"
            >
              Discuss with AI Coach
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>

        {/* Big Three */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {[
            { icon: Sun, label: "Sun Sign", sign: chart?.sun_sign, color: "text-primary" },
            { icon: Moon, label: "Moon Sign", sign: chart?.moon_sign, color: "text-muted-foreground" },
            { icon: Star, label: "Rising Sign", sign: chart?.rising_sign, color: "text-chart-2" }
          ].map(({ icon: Icon, label, sign, color }) => (
            <div key={label} className="glass-card rounded-xl p-6 card-lift" data-testid={`${label.toLowerCase().replace(' ', '-')}-card`}>
              <div className="flex items-center justify-between mb-4">
                <Icon className={`w-8 h-8 ${color}`} />
                <span className="text-2xl">{SIGN_SYMBOLS[sign]}</span>
              </div>
              <p className="text-sm text-muted-foreground mb-1">{label}</p>
              <p className="font-serif text-2xl text-foreground">{sign}</p>
              <p className={`text-sm mt-2 ${ELEMENT_COLORS[getElement(sign)]}`}>
                {getElement(sign)} Element
              </p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Planetary Positions */}
          <div className="glass-card rounded-xl p-6" data-testid="planets-card">
            <h2 className="font-serif text-xl text-foreground mb-6">Planetary Positions</h2>
            
            <div className="space-y-3">
              <TooltipProvider>
                {chart?.planets && Object.entries(chart.planets).map(([planet, data]) => {
                  // Handle different data formats
                  const sign = data?.sign || 'Unknown';
                  const degree = data?.sign_degree ?? data?.degree ?? 0;
                  const house = data?.house || '?';
                  
                  return (
                    <div 
                      key={planet}
                      className="flex items-center justify-between p-3 rounded-xl bg-muted/30 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl w-8 text-center">{PLANET_SYMBOLS[planet]}</span>
                        <div>
                          <p className="font-medium text-foreground capitalize flex items-center gap-1.5">
                            {planet.replace('_', ' ')}
                            {data?.retrograde && (
                              <span className="text-xs text-orange-400 font-mono" title="Retrograde">℞</span>
                            )}
                          </p>
                          <p className="text-xs text-muted-foreground">House {house !== null && house !== undefined ? house : '—'}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <Tooltip>
                          <TooltipTrigger>
                            <div className="text-right">
                              <p className="text-sm text-foreground">{sign}</p>
                              <p className="text-xs text-muted-foreground font-mono">{typeof degree === 'number' ? degree.toFixed(1) : degree}°</p>
                            </div>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{planet.charAt(0).toUpperCase() + planet.slice(1).replace('_', ' ')} at {typeof degree === 'number' ? degree.toFixed(1) : degree}° {sign}</p>
                          </TooltipContent>
                        </Tooltip>
                        <span className="text-xl">{SIGN_SYMBOLS[sign]}</span>
                      </div>
                    </div>
                  );
                })}
              </TooltipProvider>
            </div>
          </div>

          {/* Houses & Aspects */}
          <div className="space-y-6">
            <div className="glass-card rounded-xl p-6" data-testid="houses-card">
              <h2 className="font-serif text-xl text-foreground mb-6">House Cusps</h2>
              
              <div className="grid grid-cols-3 gap-3">
                {chart?.houses && Object.entries(chart.houses).map(([house, data]) => {
                  // Handle both old (string) and new (object) format
                  const sign = typeof data === 'string' ? data : data?.sign;
                  const degree = typeof data === 'object' ? data?.sign_degree : null;
                  return (
                    <div key={house} className="p-3 rounded-xl bg-muted/30 text-center">
                      <p className="text-xs text-muted-foreground mb-1">House {house}</p>
                      <p className="text-lg">{SIGN_SYMBOLS[sign]}</p>
                      <p className="text-xs text-foreground">{sign}</p>
                      {degree != null && <p className="text-xs text-muted-foreground">{degree.toFixed(0)}°</p>}
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="glass-card rounded-xl p-6" data-testid="aspects-card">
              <h2 className="font-serif text-xl text-foreground mb-6">Major Aspects</h2>
              
              <div className="space-y-3">
                {chart?.aspects?.map((aspect, i) => {
                  const orb = aspect.orb ?? 0;
                  const planet1 = aspect.planet1 || aspect.planet1_name;
                  const planet2 = aspect.planet2 || aspect.planet2_name;
                  const aspectType = aspect.aspect || aspect.aspect_type;
                  
                  return (
                    <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-muted/30">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{PLANET_SYMBOLS[planet1] || planet1}</span>
                        <span className="text-xs text-primary font-medium">{aspectType}</span>
                        <span className="text-lg">{PLANET_SYMBOLS[planet2] || planet2}</span>
                      </div>
                      <span className="text-xs text-muted-foreground font-mono">
                        Orb: {typeof orb === 'number' ? orb.toFixed(1) : orb}°
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {chart?.patterns?.length > 0 && (
              <div className="glass-card rounded-xl p-6" data-testid="patterns-card">
                <h2 className="font-serif text-xl text-foreground mb-4">Chart Patterns</h2>
                <div className="flex flex-wrap gap-2">
                  {chart.patterns.map((pattern, i) => (
                    <span key={i} className="zodiac-badge rounded-full px-4 py-2 text-sm">{pattern}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Numerology Section */}
            {chart?.numerology && Object.keys(chart.numerology).length > 0 && (
              <div className="glass-card rounded-xl p-6" data-testid="numerology-card">
                <h2 className="font-serif text-xl text-foreground mb-1 flex items-center gap-2">
                  <span>🔢</span> Numerology Profile
                </h2>
                <p className="text-sm text-muted-foreground mb-4">Pythagorean — derived from your name and birth date</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { key: "life_path",     label: "Life Path",     icon: "🌟" },
                    { key: "expression",    label: "Expression",    icon: "📢" },
                    { key: "soul_urge",     label: "Soul Urge",     icon: "💜" },
                    { key: "personality",   label: "Personality",   icon: "🎭" },
                    { key: "birthday",      label: "Birthday",      icon: "🎂" },
                    { key: "personal_year", label: "Personal Year", icon: "📅" },
                    { key: "first_name",    label: "First Name",    icon: "✨" },
                    { key: "last_name",     label: "Family Name",   icon: "🌳" },
                  ].map(({ key, label, icon }) => {
                    const entry = chart.numerology[key];
                    if (!entry || !entry.number) return null;
                    const isMaster = [11, 22, 33].includes(entry.number);
                    return (
                      <TooltipProvider key={key}>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <div className="p-4 rounded-xl bg-muted/30 text-center cursor-default hover:bg-muted/50 transition-colors">
                              <div className="text-lg mb-1">{icon}</div>
                              <div className={`text-2xl font-bold mb-1 ${isMaster ? "text-yellow-400" : "text-primary"}`}>
                                {entry.number}
                                {isMaster && <span className="text-xs ml-0.5">✦</span>}
                              </div>
                              <div className="text-xs text-muted-foreground">{label}</div>
                              <div className="text-xs font-medium text-foreground mt-0.5">{entry.keyword}</div>
                            </div>
                          </TooltipTrigger>
                          <TooltipContent side="top" className="max-w-xs text-center">
                            <p className="font-semibold">{label} {entry.number} — {entry.keyword}</p>
                            <p className="text-xs mt-1">{entry.theme}</p>
                            {isMaster && <p className="text-xs text-yellow-400 mt-1">✦ Master Number — not reduced further</p>}
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
