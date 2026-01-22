import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Sparkles, 
  Send, 
  ArrowLeft,
  MessageCircle,
  Plus,
  Clock,
  User
} from "lucide-react";
import { toast } from "sonner";

export default function ChatPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const response = await axios.get(`${API}/chat/sessions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(response.data);
    } catch (error) {
      console.error("Error fetching sessions:", error);
    }
  };

  const loadSession = async (sid) => {
    try {
      const response = await axios.get(`${API}/chat/history/${sid}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data);
      setSessionId(sid);
    } catch (error) {
      console.error("Error loading session:", error);
    }
  };

  const startNewSession = () => {
    setMessages([]);
    setSessionId(null);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage, timestamp: new Date().toISOString() }]);
    setLoading(true);

    try {
      const response = await axios.post(
        `${API}/chat`,
        { message: userMessage, session_id: sessionId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: response.data.response,
        timestamp: new Date().toISOString()
      }]);
      
      if (!sessionId) {
        setSessionId(response.data.session_id);
        fetchSessions();
      }
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to get response. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cosmic-void flex">
      {/* Sessions Sidebar */}
      <aside className="w-72 bg-black/40 border-r border-white/5 flex flex-col h-screen">
        <div className="p-4 border-b border-white/5">
          <Link to="/dashboard" className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">Back to Dashboard</span>
          </Link>
          
          <Button 
            className="w-full bg-primary/10 text-primary hover:bg-primary/20"
            onClick={startNewSession}
            data-testid="new-chat-btn"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Conversation
          </Button>
        </div>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-2">
            {sessions.map((session) => (
              <button
                key={session.session_id}
                onClick={() => loadSession(session.session_id)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  sessionId === session.session_id 
                    ? 'bg-primary/10 border border-primary/20' 
                    : 'hover:bg-white/5'
                }`}
                data-testid={`session-${session.session_id}`}
              >
                <p className="text-sm text-cosmic-starlight truncate mb-1">
                  {session.preview}...
                </p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="w-3 h-3" />
                  {new Date(session.timestamp).toLocaleDateString()}
                </div>
              </button>
            ))}
            
            {sessions.length === 0 && (
              <div className="text-center py-8">
                <MessageCircle className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">No conversations yet</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </aside>

      {/* Chat Area */}
      <main className="flex-1 flex flex-col h-screen">
        {/* Header */}
        <header className="p-4 border-b border-white/5 bg-black/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="font-medium text-cosmic-starlight">Gab44 AI Coach</h1>
              <p className="text-xs text-green-400 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-400" />
                Online - Ready to guide you
              </p>
            </div>
          </div>
        </header>

        {/* Messages */}
        <ScrollArea className="flex-1 p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.length === 0 && (
              <div className="text-center py-16">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-primary" />
                </div>
                <h2 className="font-serif text-xl text-cosmic-starlight mb-2">
                  Hello, {user?.name?.split(" ")[0]}
                </h2>
                <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                  I'm your personal astrology AI coach. Ask me anything about your chart, 
                  transits, relationships, career timing, or life guidance.
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {[
                    "What should I focus on today?",
                    "Tell me about my career path",
                    "What's happening in my chart?",
                    "Relationship guidance"
                  ].map((prompt) => (
                    <Button
                      key={prompt}
                      variant="outline"
                      className="border-white/10 text-sm"
                      onClick={() => setInput(prompt)}
                      data-testid={`prompt-${prompt.replace(/\s+/g, '-').toLowerCase()}`}
                    >
                      {prompt}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div 
                key={index}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-4 h-4 text-primary" />
                  </div>
                )}
                
                <div 
                  className={`max-w-xl rounded-2xl p-4 ${
                    message.role === 'user' 
                      ? 'chat-bubble-user rounded-tr-sm' 
                      : 'chat-bubble-assistant rounded-tl-sm'
                  }`}
                  data-testid={`message-${index}`}
                >
                  <p className="text-sm text-cosmic-starlight whitespace-pre-wrap leading-relaxed">
                    {message.content}
                  </p>
                </div>

                {message.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-muted-foreground" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-primary animate-pulse" />
                </div>
                <div className="chat-bubble-assistant rounded-2xl rounded-tl-sm p-4">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t border-white/5 bg-black/20">
          <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask your AI coach anything..."
              className="flex-1 bg-black/30 border-white/10 h-12"
              disabled={loading}
              data-testid="chat-input"
            />
            <Button 
              type="submit" 
              className="bg-primary text-primary-foreground h-12 px-6"
              disabled={loading || !input.trim()}
              data-testid="send-btn"
            >
              <Send className="w-5 h-5" />
            </Button>
          </form>
        </div>
      </main>
    </div>
  );
}
