import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { Sparkles, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function VerifyEmailPage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) {
      setStatus("error");
      setMessage("No verification token found in the link.");
      return;
    }
    axios
      .get(`${API}/auth/verify-email`, { params: { token } })
      .then(() => {
        setStatus("success");
        setMessage("Your email has been verified! You can now log in.");
      })
      .catch((err) => {
        setStatus("error");
        setMessage(
          err.response?.data?.detail ||
            "This link is invalid or has already been used."
        );
      });
  }, []);

  return (
    <div className="min-h-screen bg-background cosmic-page-bg flex items-center justify-center p-8">
      <div className="glass-card rounded-2xl p-10 max-w-md w-full text-center space-y-6">
        <div className="flex items-center justify-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <span className="font-serif text-xl text-foreground">Gab44</span>
        </div>

        {status === "loading" && (
          <>
            <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto" />
            <p className="text-muted-foreground">Verifying your email…</p>
          </>
        )}

        {status === "success" && (
          <>
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
            <h1 className="font-serif text-2xl text-foreground">Email Verified ✨</h1>
            <p className="text-muted-foreground">{message}</p>
            <Button className="w-full rounded-xl" onClick={() => navigate("/auth")}>
              Sign In
            </Button>
          </>
        )}

        {status === "error" && (
          <>
            <XCircle className="w-12 h-12 text-destructive mx-auto" />
            <h1 className="font-serif text-2xl text-foreground">Verification Failed</h1>
            <p className="text-muted-foreground">{message}</p>
            <div className="flex flex-col gap-3">
              <Button className="w-full rounded-xl" onClick={() => navigate("/auth")}>
                Back to Sign In
              </Button>
              <p className="text-xs text-muted-foreground">
                After signing in, go to{" "}
                <span className="text-primary">Settings → Account</span> to resend the verification link.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
