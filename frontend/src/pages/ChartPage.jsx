import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { 
  Sparkles, 
  ArrowLeft,
  Sun,
  Moon,
  Star,
  ChevronRight,
  Info
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const PLANET_SYMBOLS = {
  sun: "☉",
  moon: "☽",
  mercury: "☿",
  venus: "♀",
  mars: "♂",
  jupiter: "♃",
  saturn: "♄",
  uranus: "♅",
  neptune: "♆",
  pluto: "♇"
};

const SIGN_SYMBOLS = {
  Aries: "♈",
  Taurus: "♉",
  Gemini: "♊",
  Cancer: "♋",
  Leo: "♌",
  Virgo: "♍",
  Libra: "♎",
  Scorpio: "♏",
  Sagittarius: "♐",
  Capricorn: "♑",
  Aquarius: "♒",
  Pisces: "♓"
};

const ELEMENT_COLORS = {
  Fire: "text-orange-400",
  Earth: "text-green-400",
  Air: "text-cyan-400",
  Water: "text-blue-400"
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

export default function ChartPage() {
  const { user, token } = useAuth();
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
      <div className="min-h-screen bg-cosmic-void flex items-center justify-center">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-primary/40" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cosmic-void p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link to="/dashboard" className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-4">
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back to Dashboard</span>
            </Link>
            <h1 className="font-serif text-3xl text-cosmic-starlight">Your Birth Chart</h1>
            <p className="text-muted-foreground">
              Born {user?.birth_date} in {user?.birth_place}
            </p>
          </div>
          
          <Button 
            onClick={() => navigate("/chat")}
            className="bg-primary/10 text-primary hover:bg-primary/20"
            data-testid="discuss-chart-btn"
          >
            Discuss with AI Coach
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>

        {/* Big Three */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="glass-card rounded-xl p-6" data-testid="sun-sign-card">
            <div className="flex items-center justify-between mb-4">
              <Sun className="w-8 h-8 text-primary" />
              <span className="text-2xl">{SIGN_SYMBOLS[chart?.sun_sign]}</span>
            </div>
            <p className="text-sm text-muted-foreground mb-1">Sun Sign</p>
            <p className="font-serif text-2xl text-cosmic-starlight">{chart?.sun_sign}</p>
            <p className={`text-sm mt-2 ${ELEMENT_COLORS[getElement(chart?.sun_sign)]}`}>
              {getElement(chart?.sun_sign)} Element
            </p>
          </div>

          <div className="glass-card rounded-xl p-6" data-testid="moon-sign-card">
            <div className="flex items-center justify-between mb-4">
              <Moon className="w-8 h-8 text-cosmic-silver" />
              <span className="text-2xl">{SIGN_SYMBOLS[chart?.moon_sign]}</span>
            </div>
            <p className="text-sm text-muted-foreground mb-1">Moon Sign</p>
            <p className="font-serif text-2xl text-cosmic-starlight">{chart?.moon_sign}</p>
            <p className={`text-sm mt-2 ${ELEMENT_COLORS[getElement(chart?.moon_sign)]}`}>
              {getElement(chart?.moon_sign)} Element
            </p>
          </div>

          <div className="glass-card rounded-xl p-6" data-testid="rising-sign-card">
            <div className="flex items-center justify-between mb-4">
              <Star className="w-8 h-8 text-cosmic-nebula" />
              <span className="text-2xl">{SIGN_SYMBOLS[chart?.rising_sign]}</span>
            </div>
            <p className="text-sm text-muted-foreground mb-1">Rising Sign</p>
            <p className="font-serif text-2xl text-cosmic-starlight">{chart?.rising_sign}</p>
            <p className={`text-sm mt-2 ${ELEMENT_COLORS[getElement(chart?.rising_sign)]}`}>
              {getElement(chart?.rising_sign)} Element
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Planetary Positions */}
          <div className="glass-card rounded-xl p-6" data-testid="planets-card">
            <h2 className="font-serif text-xl text-cosmic-starlight mb-6">Planetary Positions</h2>
            
            <div className="space-y-4">
              <TooltipProvider>
                {chart?.planets && Object.entries(chart.planets).map(([planet, data]) => (
                  <div 
                    key={planet}
                    className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl w-8 text-center">{PLANET_SYMBOLS[planet]}</span>
                      <div>
                        <p className="font-medium text-cosmic-starlight capitalize">{planet}</p>
                        <p className="text-xs text-muted-foreground">House {data.house}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <Tooltip>
                        <TooltipTrigger>
                          <div className="text-right">
                            <p className="text-sm text-cosmic-starlight">{data.sign}</p>
                            <p className="text-xs text-muted-foreground font-mono">{data.degree.toFixed(1)}°</p>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>{planet.charAt(0).toUpperCase() + planet.slice(1)} at {data.degree.toFixed(1)}° {data.sign}</p>
                        </TooltipContent>
                      </Tooltip>
                      <span className="text-xl">{SIGN_SYMBOLS[data.sign]}</span>
                    </div>
                  </div>
                ))}
              </TooltipProvider>
            </div>
          </div>

          {/* Houses */}
          <div className="space-y-6">
            <div className="glass-card rounded-xl p-6" data-testid="houses-card">
              <h2 className="font-serif text-xl text-cosmic-starlight mb-6">House Cusps</h2>
              
              <div className="grid grid-cols-3 gap-3">
                {chart?.houses && Object.entries(chart.houses).map(([house, sign]) => (
                  <div 
                    key={house}
                    className="p-3 rounded-lg bg-white/5 text-center"
                  >
                    <p className="text-xs text-muted-foreground mb-1">House {house}</p>
                    <p className="text-lg">{SIGN_SYMBOLS[sign]}</p>
                    <p className="text-xs text-cosmic-starlight">{sign}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Aspects */}
            <div className="glass-card rounded-xl p-6" data-testid="aspects-card">
              <h2 className="font-serif text-xl text-cosmic-starlight mb-6">Major Aspects</h2>
              
              <div className="space-y-3">
                {chart?.aspects?.map((aspect, i) => (
                  <div 
                    key={i}
                    className="flex items-center justify-between p-3 rounded-lg bg-white/5"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{PLANET_SYMBOLS[aspect.planet1]}</span>
                      <span className="text-xs text-primary">{aspect.aspect}</span>
                      <span className="text-lg">{PLANET_SYMBOLS[aspect.planet2]}</span>
                    </div>
                    <span className="text-xs text-muted-foreground font-mono">
                      Orb: {aspect.orb.toFixed(1)}°
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Patterns */}
            {chart?.patterns?.length > 0 && (
              <div className="glass-card rounded-xl p-6" data-testid="patterns-card">
                <h2 className="font-serif text-xl text-cosmic-starlight mb-4">Chart Patterns</h2>
                
                <div className="flex flex-wrap gap-2">
                  {chart.patterns.map((pattern, i) => (
                    <span 
                      key={i}
                      className="zodiac-badge rounded-full px-4 py-2 text-sm"
                    >
                      {pattern}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
