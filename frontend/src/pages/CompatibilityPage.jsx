import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTheme } from "@/context/ThemeContext";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import {
  Heart,
  Sparkles,
  ArrowLeft,
  Sun,
  Moon,
  Users,
  MessageCircle,
  Zap,
  Star,
  TrendingUp,
  Clock,
  ChevronRight,
  Plus,
  Loader2,
  HeartHandshake,
  Flame,
  Brain,
  Shield,
  Target
} from "lucide-react";

const CATEGORY_CONFIG = {
  romantic: { icon: Flame, color: "text-rose-500", bg: "bg-rose-500/10", label: "Romance" },
  emotional: { icon: Heart, color: "text-pink-500", bg: "bg-pink-500/10", label: "Emotional" },
  communication: { icon: MessageCircle, color: "text-blue-500", bg: "bg-blue-500/10", label: "Communication" },
  stability: { icon: Shield, color: "text-emerald-500", bg: "bg-emerald-500/10", label: "Stability" },
  karmic: { icon: Sparkles, color: "text-purple-500", bg: "bg-purple-500/10", label: "Karmic" }
};

const ScoreRing = ({ score, size = 120, label }) => {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  const getColor = (score) => {
    if (score >= 80) return "#22c55e";
    if (score >= 60) return "#eab308";
    return "#ef4444";
  };

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-muted/20"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor(score)}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-serif text-3xl text-foreground">{Math.round(score)}%</span>
        {label && <span className="text-xs text-muted-foreground mt-1">{label}</span>}
      </div>
    </div>
  );
};

const CategoryScore = ({ category, score }) => {
  const config = CATEGORY_CONFIG[category] || { icon: Star, color: "text-primary", bg: "bg-primary/10", label: category };
  const Icon = config.icon;
  
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-muted/30">
      <div className={`w-10 h-10 rounded-lg ${config.bg} flex items-center justify-center`}>
        <Icon className={`w-5 h-5 ${config.color}`} />
      </div>
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-medium text-foreground">{config.label}</span>
          <span className="text-sm text-muted-foreground">{Math.round(score)}%</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div 
            className="h-full bg-primary rounded-full transition-all duration-500"
            style={{ width: `${score}%` }}
          />
        </div>
      </div>
    </div>
  );
};

const ReportCard = ({ report, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="w-full glass-card rounded-xl p-4 text-left hover:border-primary/30 transition-all group"
    >
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-rose-500/20 to-purple-500/20 flex items-center justify-center">
          <Heart className="w-6 h-6 text-rose-500" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-foreground truncate">{report.partner_name}</h3>
          <p className="text-sm text-muted-foreground">{report.partner_sun_sign} Sun</p>
        </div>
        <div className="text-right">
          <div className="font-serif text-xl text-primary">{Math.round(report.overall_score)}%</div>
          <p className="text-xs text-muted-foreground">
            {new Date(report.created_at).toLocaleDateString()}
          </p>
        </div>
        <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
      </div>
    </button>
  );
};

export default function CompatibilityPage() {
  const { token, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    partner_name: "",
    partner_birth_date: "",
    partner_birth_time: "",
    partner_birth_place: ""
  });

  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const res = await axios.get(`${API}/compatibility/reports`, authHeaders);
      setReports(res.data);
      if (res.data.length > 0 && !selectedReport) {
        setSelectedReport(res.data[0]);
      }
    } catch (error) {
      console.error("Error fetching reports:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!formData.partner_name || !formData.partner_birth_date || !formData.partner_birth_place) {
      toast.error("Please fill in all required fields");
      return;
    }

    setAnalyzing(true);
    try {
      const res = await axios.post(`${API}/compatibility/analyze`, formData, authHeaders);
      setSelectedReport(res.data);
      setReports(prev => [res.data, ...prev]);
      setShowForm(false);
      setFormData({ partner_name: "", partner_birth_date: "", partner_birth_time: "", partner_birth_place: "" });
      toast.success("Compatibility analysis complete!");
    } catch (error) {
      console.error("Analysis error:", error);
      toast.error("Failed to analyze compatibility");
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse-glow w-16 h-16 rounded-full bg-rose-500/20 flex items-center justify-center">
          <Heart className="w-8 h-8 text-rose-500 animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-header border-b border-border/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm hidden sm:inline">Dashboard</span>
              </Link>
              <div className="h-6 w-px bg-border" />
              <div className="flex items-center gap-2">
                <Heart className="w-5 h-5 text-rose-500" />
                <h1 className="font-serif text-lg text-foreground">Compatibility</h1>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                onClick={() => setShowForm(true)}
                className="gap-2 rounded-xl bg-gradient-to-r from-rose-500 to-purple-500 hover:from-rose-600 hover:to-purple-600"
                data-testid="new-analysis-btn"
              >
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">New Analysis</span>
              </Button>
              <button
                onClick={toggleTheme}
                className="w-10 h-10 rounded-xl bg-muted/50 flex items-center justify-center"
              >
                {theme === "dark" ? <Sun className="w-5 h-5 text-primary" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* New Analysis Form Modal */}
        {showForm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="glass-card rounded-2xl p-6 w-full max-w-md" data-testid="analysis-form">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500/20 to-purple-500/20 flex items-center justify-center">
                  <HeartHandshake className="w-6 h-6 text-rose-500" />
                </div>
                <div>
                  <h2 className="font-serif text-xl text-foreground">New Compatibility Analysis</h2>
                  <p className="text-sm text-muted-foreground">Enter your partner's birth details</p>
                </div>
              </div>

              <form onSubmit={handleAnalyze} className="space-y-4">
                <div>
                  <Label htmlFor="partner_name">Partner's Name *</Label>
                  <Input
                    id="partner_name"
                    value={formData.partner_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, partner_name: e.target.value }))}
                    placeholder="Enter name"
                    className="mt-1 rounded-xl"
                    data-testid="partner-name-input"
                  />
                </div>

                <div>
                  <Label htmlFor="partner_birth_date">Birth Date *</Label>
                  <Input
                    id="partner_birth_date"
                    type="date"
                    value={formData.partner_birth_date}
                    onChange={(e) => setFormData(prev => ({ ...prev, partner_birth_date: e.target.value }))}
                    className="mt-1 rounded-xl"
                    data-testid="partner-birth-date-input"
                  />
                </div>

                <div>
                  <Label htmlFor="partner_birth_time">Birth Time (optional)</Label>
                  <Input
                    id="partner_birth_time"
                    type="time"
                    value={formData.partner_birth_time}
                    onChange={(e) => setFormData(prev => ({ ...prev, partner_birth_time: e.target.value }))}
                    className="mt-1 rounded-xl"
                    data-testid="partner-birth-time-input"
                  />
                </div>

                <div>
                  <Label htmlFor="partner_birth_place">Birth Place *</Label>
                  <Input
                    id="partner_birth_place"
                    value={formData.partner_birth_place}
                    onChange={(e) => setFormData(prev => ({ ...prev, partner_birth_place: e.target.value }))}
                    placeholder="City, Country"
                    className="mt-1 rounded-xl"
                    data-testid="partner-birth-place-input"
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowForm(false)}
                    className="flex-1 rounded-xl"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={analyzing}
                    className="flex-1 rounded-xl bg-gradient-to-r from-rose-500 to-purple-500 hover:from-rose-600 hover:to-purple-600"
                    data-testid="analyze-btn"
                  >
                    {analyzing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        Analyze
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Reports List */}
          <div className="lg:col-span-1 space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-medium text-foreground">Your Reports</h2>
              <span className="text-sm text-muted-foreground">{reports.length} total</span>
            </div>

            {reports.length === 0 ? (
              <div className="glass-card rounded-xl p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-rose-500/10 flex items-center justify-center mx-auto mb-4">
                  <Heart className="w-8 h-8 text-rose-500" />
                </div>
                <h3 className="font-medium text-foreground mb-2">No reports yet</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Discover your cosmic connection with someone special
                </p>
                <Button
                  onClick={() => setShowForm(true)}
                  className="rounded-xl bg-gradient-to-r from-rose-500 to-purple-500"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Report
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {reports.map((report) => (
                  <ReportCard
                    key={report.id}
                    report={report}
                    onClick={() => setSelectedReport(report)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Report Detail */}
          <div className="lg:col-span-2">
            {selectedReport ? (
              <div className="space-y-6">
                {/* Header Card */}
                <div className="glass-card rounded-2xl p-6">
                  <div className="flex flex-col sm:flex-row items-center gap-6">
                    {/* You */}
                    <div className="text-center">
                      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary/20 to-primary/40 flex items-center justify-center mx-auto mb-2">
                        <span className="font-serif text-2xl text-primary">{user?.name?.[0] || "Y"}</span>
                      </div>
                      <p className="font-medium text-foreground">{user?.name || "You"}</p>
                      <p className="text-sm text-muted-foreground">{user?.sun_sign} Sun</p>
                    </div>

                    {/* Score */}
                    <div className="flex-1 flex flex-col items-center">
                      <ScoreRing score={selectedReport.overall_score} label="Overall" />
                      <div className="mt-4 text-center">
                        <p className="text-sm text-muted-foreground">
                          {selectedReport.element_compatibility?.description}
                        </p>
                      </div>
                    </div>

                    {/* Partner */}
                    <div className="text-center">
                      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-rose-500/20 to-purple-500/40 flex items-center justify-center mx-auto mb-2">
                        <span className="font-serif text-2xl text-rose-500">{selectedReport.partner_name?.[0] || "P"}</span>
                      </div>
                      <p className="font-medium text-foreground">{selectedReport.partner_name}</p>
                      <p className="text-sm text-muted-foreground">{selectedReport.partner_sun_sign} Sun</p>
                    </div>
                  </div>
                </div>

                {/* Category Scores */}
                <div className="glass-card rounded-2xl p-6">
                  <h3 className="font-medium text-foreground mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-primary" />
                    Compatibility Breakdown
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {selectedReport.category_scores && Object.entries(selectedReport.category_scores).map(([category, score]) => (
                      <CategoryScore key={category} category={category} score={score} />
                    ))}
                  </div>
                </div>

                {/* Strengths & Challenges */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="glass-card rounded-2xl p-6">
                    <h3 className="font-medium text-foreground mb-4 flex items-center gap-2">
                      <Star className="w-5 h-5 text-amber-500" />
                      Strengths
                    </h3>
                    <ul className="space-y-3">
                      {selectedReport.strengths?.map((strength, i) => (
                        <li key={i} className="flex items-start gap-3 text-sm">
                          <div className="w-2 h-2 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                          <span className="text-muted-foreground">{strength}</span>
                        </li>
                      ))}
                      {(!selectedReport.strengths || selectedReport.strengths.length === 0) && (
                        <li className="text-sm text-muted-foreground">Natural harmony detected in your charts</li>
                      )}
                    </ul>
                  </div>

                  <div className="glass-card rounded-2xl p-6">
                    <h3 className="font-medium text-foreground mb-4 flex items-center gap-2">
                      <Target className="w-5 h-5 text-blue-500" />
                      Growth Areas
                    </h3>
                    <ul className="space-y-3">
                      {selectedReport.challenges?.map((challenge, i) => (
                        <li key={i} className="flex items-start gap-3 text-sm">
                          <div className="w-2 h-2 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                          <span className="text-muted-foreground">{challenge}</span>
                        </li>
                      ))}
                      {(!selectedReport.challenges || selectedReport.challenges.length === 0) && (
                        <li className="text-sm text-muted-foreground">Embrace differences as complementary strengths</li>
                      )}
                    </ul>
                  </div>
                </div>

                {/* AI Analysis */}
                <div className="glass-card rounded-2xl p-6">
                  <h3 className="font-medium text-foreground mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-purple-500" />
                    AI Relationship Analysis
                  </h3>
                  <div className="prose prose-sm max-w-none text-muted-foreground">
                    {selectedReport.ai_analysis?.split('\n').map((paragraph, i) => (
                      paragraph.trim() && <p key={i} className="mb-3 last:mb-0">{paragraph}</p>
                    ))}
                  </div>
                </div>

                {/* Synastry Aspects */}
                {selectedReport.synastry_aspects && selectedReport.synastry_aspects.length > 0 && (
                  <div className="glass-card rounded-2xl p-6">
                    <h3 className="font-medium text-foreground mb-4 flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-primary" />
                      Key Synastry Aspects
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {selectedReport.synastry_aspects.slice(0, 9).map((aspect, i) => {
                        const config = CATEGORY_CONFIG[aspect.category] || CATEGORY_CONFIG.romantic;
                        return (
                          <div key={i} className="p-3 rounded-xl bg-muted/30 border border-border/50">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium text-foreground capitalize">
                                {aspect.person1_planet}
                              </span>
                              <span className={`text-xs px-2 py-0.5 rounded-full ${config.bg} ${config.color}`}>
                                {aspect.aspect_type}
                              </span>
                              <span className="text-sm font-medium text-foreground capitalize">
                                {aspect.person2_planet}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-primary rounded-full"
                                  style={{ width: `${aspect.harmony * 100}%` }}
                                />
                              </div>
                              <span className="text-xs text-muted-foreground">{Math.round(aspect.harmony * 100)}%</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Karmic Themes */}
                {selectedReport.karmic_themes && selectedReport.karmic_themes.length > 0 && (
                  <div className="glass-card rounded-2xl p-6 bg-gradient-to-br from-purple-500/5 to-transparent">
                    <h3 className="font-medium text-foreground mb-4 flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-purple-500" />
                      Karmic & Spiritual Themes
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedReport.karmic_themes.map((theme, i) => (
                        <span key={i} className="px-4 py-2 rounded-full bg-purple-500/10 text-purple-500 text-sm">
                          {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-card rounded-2xl p-12 text-center">
                <div className="w-20 h-20 rounded-full bg-rose-500/10 flex items-center justify-center mx-auto mb-6">
                  <HeartHandshake className="w-10 h-10 text-rose-500" />
                </div>
                <h3 className="font-serif text-2xl text-foreground mb-3">Discover Your Connection</h3>
                <p className="text-muted-foreground max-w-md mx-auto mb-6">
                  Uncover the cosmic blueprint of your relationship. Our AI-powered synastry analysis reveals
                  the strengths, challenges, and growth opportunities in your connection.
                </p>
                <Button
                  onClick={() => setShowForm(true)}
                  size="lg"
                  className="rounded-xl bg-gradient-to-r from-rose-500 to-purple-500 hover:from-rose-600 hover:to-purple-600"
                >
                  <Heart className="w-5 h-5 mr-2" />
                  Start Analysis
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
