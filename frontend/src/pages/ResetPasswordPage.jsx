import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { parseApiError } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Sparkles, Eye, EyeOff, CheckCircle, XCircle } from "lucide-react";

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [tokenInvalid, setTokenInvalid] = useState(false);

  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get("token");
    if (!t) {
      setTokenInvalid(true);
    } else {
      setToken(t);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm) {
      toast.error("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API}/auth/reset-password`, { token, new_password: password });
      setDone(true);
      toast.success("Password updated! You can now sign in.");
    } catch (err) {
      toast.error(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background cosmic-page-bg flex items-center justify-center p-8">
      <div className="glass-card rounded-2xl p-10 max-w-md w-full space-y-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <span className="font-serif text-xl text-foreground">Gab44</span>
        </div>

        {tokenInvalid && (
          <>
            <XCircle className="w-12 h-12 text-destructive mx-auto" />
            <h1 className="font-serif text-2xl text-foreground text-center">Invalid Link</h1>
            <p className="text-muted-foreground text-center">This reset link is missing or invalid. Please request a new one.</p>
            <Button className="w-full rounded-xl" onClick={() => navigate("/auth")}>Back to Sign In</Button>
          </>
        )}

        {!tokenInvalid && !done && (
          <>
            <h1 className="font-serif text-2xl text-foreground">Choose a new password</h1>
            <p className="text-muted-foreground text-sm">Min. 8 characters, must include a letter and a digit or special character.</p>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="new-password">New Password</Label>
                <div className="relative">
                  <Input
                    id="new-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-muted/30 border-border h-12 rounded-xl pr-10"
                    required
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirm Password</Label>
                <Input
                  id="confirm-password"
                  type="password"
                  placeholder="••••••••"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  className="bg-muted/30 border-border h-12 rounded-xl"
                  required
                />
              </div>
              <Button type="submit" disabled={loading} className="w-full glow-button bg-primary text-primary-foreground h-12 rounded-xl">
                {loading
                  ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />Saving...</span>
                  : "Set New Password"}
              </Button>
            </form>
          </>
        )}

        {done && (
          <>
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
            <h1 className="font-serif text-2xl text-foreground text-center">Password Updated ✨</h1>
            <p className="text-muted-foreground text-center">Your password has been changed. You can now sign in.</p>
            <Button className="w-full rounded-xl" onClick={() => navigate("/auth")}>Sign In</Button>
          </>
        )}
      </div>
    </div>
  );
}
