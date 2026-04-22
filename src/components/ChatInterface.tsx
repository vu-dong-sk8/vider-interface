import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send, Paperclip, Mic, Smile, RotateCcw, Plus, Search,
  MessageSquare, Clock, Zap, Settings, ChevronLeft, ChevronRight,
  Bot, User, Sparkles, Hash, PanelLeftClose, PanelRightClose,
  AlertCircle, Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "@tanstack/react-router";
import { sendMessage, checkHealth } from "@/lib/chatApi";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface Message {
  id: number;
  role: "user" | "bot";
  content: string;
  time: string;
  error?: boolean;
}

/* ------------------------------------------------------------------ */
/* Static data                                                         */
/* ------------------------------------------------------------------ */

const conversations = [
  { id: 1, title: "Viết email sản phẩm", time: "Hôm nay", active: true },
  { id: 2, title: "Phân tích dữ liệu Q4", time: "Hôm qua", active: false },
  { id: 3, title: "Tóm tắt báo cáo tài chính", time: "3 ngày trước", active: false },
  { id: 4, title: "Brainstorm marketing", time: "1 tuần trước", active: false },
];

const suggestedPrompts = [
  "Tóm tắt tài liệu",
  "Viết code Python",
  "Dịch sang tiếng Anh",
  "Phân tích dữ liệu",
];

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function currentTime(): string {
  return new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
}

// Simple username — in production you'd use auth
const USERNAME = "user";

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "bot",
      content:
        "Xin chào! Tôi là VIDER — trợ lý AI của bạn. Hãy cho tôi biết bạn cần hỗ trợ gì nhé.",
      time: "10:00",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Check backend health on mount
  useEffect(() => {
    checkHealth().then(setBackendOnline);
  }, []);

  // ------------------------------------------------------------------
  // Send handler — calls the real backend API
  // ------------------------------------------------------------------
  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || isTyping) return;

    const userMsg: Message = {
      id: Date.now(),
      role: "user",
      content: text,
      time: currentTime(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      // Build chat history for the API (last messages in simple format)
      const history = messages
        .filter((m) => !m.error)
        .map((m) => ({
          role: m.role === "bot" ? "assistant" : "user",
          content: m.content,
        }));

      // Add the current user message
      history.push({ role: "user", content: text });

      const response = await sendMessage(USERNAME, text);

      const botMsg: Message = {
        id: Date.now() + 1,
        role: "bot",
        content: response.reply,
        time: currentTime(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorText =
        err instanceof Error
          ? err.message
          : "Không thể kết nối tới server. Hãy kiểm tra backend đang chạy.";

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "bot",
          content: `⚠️ Lỗi: ${errorText}`,
          time: currentTime(),
          error: true,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }, [input, isTyping, messages]);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top bar */}
      <div className="h-14 border-b border-border flex items-center justify-between px-4 bg-card shrink-0">
        <div className="flex items-center gap-3">
          <Link to="/" className="text-display text-lg tracking-widest">VIDER</Link>
          <span className="text-label text-vider-accent text-[10px] px-2 py-0.5 rounded-full border border-vider-accent/30">BETA</span>
        </div>
        <div className="flex items-center gap-2">
          {/* Backend status indicator */}
          {backendOnline !== null && (
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mr-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  backendOnline ? "bg-green-500" : "bg-red-500"
                }`}
              />
              {backendOnline ? "Backend Online" : "Backend Offline"}
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setLeftOpen(!leftOpen)}
            className="hidden md:flex"
            aria-label="Toggle left panel"
          >
            <PanelLeftClose className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setRightOpen(!rightOpen)}
            className="hidden lg:flex"
            aria-label="Toggle right panel"
          >
            <PanelRightClose className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon" aria-label="Settings">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <AnimatePresence>
          {leftOpen && (
            <motion.aside
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 280, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="hidden md:flex flex-col border-r border-border bg-surface-sunken overflow-hidden shrink-0"
            >
              <div className="p-4">
                <Button variant="outline" className="w-full justify-start gap-2 text-sm">
                  <Plus className="w-4 h-4" />
                  Cuộc trò chuyện mới
                </Button>
              </div>

              <div className="px-4 pb-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Tìm kiếm..."
                    className="w-full h-9 pl-9 pr-3 rounded-md border border-border bg-background text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                  />
                </div>
              </div>

              <div className="flex-1 overflow-y-auto px-2">
                <p className="text-label text-muted-foreground px-2 py-2">Gần đây</p>
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    className={`w-full text-left px-3 py-2.5 rounded-md text-sm transition-colors duration-150 flex items-start gap-2.5 mb-0.5 ${
                      conv.active
                        ? "bg-card border border-border vider-shadow"
                        : "hover:bg-card/50"
                    }`}
                  >
                    <MessageSquare className="w-4 h-4 mt-0.5 shrink-0 text-muted-foreground" />
                    <div className="min-w-0">
                      <p className={`truncate ${conv.active ? "font-medium text-foreground" : "text-foreground/80"}`}>
                        {conv.title}
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">{conv.time}</p>
                    </div>
                  </button>
                ))}
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Backend offline banner */}
          {backendOnline === false && (
            <div className="bg-destructive/10 border-b border-destructive/20 px-4 py-2 flex items-center gap-2 text-sm text-destructive shrink-0">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>
                Backend không phản hồi. Hãy chắc chắn chạy{" "}
                <code className="px-1.5 py-0.5 rounded bg-destructive/10 font-mono text-xs">
                  python main.py
                </code>{" "}
                trong thư mục <code className="px-1.5 py-0.5 rounded bg-destructive/10 font-mono text-xs">vider-backend</code>.
              </span>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                  className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  {msg.role === "bot" && (
                    <div className={`w-8 h-8 rounded-md flex items-center justify-center shrink-0 mt-1 ${
                      msg.error ? "bg-destructive" : "bg-foreground"
                    }`}>
                      {msg.error ? (
                        <AlertCircle className="w-4 h-4 text-background" />
                      ) : (
                        <Bot className="w-4 h-4 text-background" />
                      )}
                    </div>
                  )}
                  <div className={`max-w-[75%] ${msg.role === "user" ? "order-first" : ""}`}>
                    <div
                      className={`px-4 py-3 rounded-xl text-sm leading-relaxed whitespace-pre-wrap ${
                        msg.role === "user"
                          ? "bg-foreground text-background rounded-br-sm"
                          : msg.error
                            ? "bg-destructive/10 border border-destructive/30 text-destructive rounded-bl-sm"
                            : "bg-surface-sunken border border-border rounded-bl-sm"
                      }`}
                    >
                      {msg.content}
                    </div>
                    <p className={`text-[10px] text-muted-foreground mt-1.5 ${msg.role === "user" ? "text-right" : "text-left"}`}>
                      {msg.time}
                    </p>
                  </div>
                  {msg.role === "user" && (
                    <div className="w-8 h-8 rounded-md bg-vider-accent flex items-center justify-center shrink-0 mt-1">
                      <User className="w-4 h-4 text-vider-accent-foreground" />
                    </div>
                  )}
                </motion.div>
              ))}

              {/* Typing indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-3"
                >
                  <div className="w-8 h-8 rounded-md bg-foreground flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-background" />
                  </div>
                  <div className="bg-surface-sunken border border-border rounded-xl px-4 py-3 rounded-bl-sm">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">VIDER đang suy nghĩ...</span>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input area */}
          <div className="border-t border-border bg-card p-4 shrink-0">
            <div className="max-w-3xl mx-auto">
              <div className="flex items-end gap-2 bg-background border border-border rounded-xl px-4 py-3 focus-within:ring-1 focus-within:ring-ring transition-shadow">
                <div className="flex gap-1 shrink-0">
                  <button className="p-1.5 rounded-md hover:bg-muted transition-colors" aria-label="Attach file">
                    <Paperclip className="w-4 h-4 text-muted-foreground" />
                  </button>
                </div>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder={isTyping ? "Đang chờ phản hồi..." : "Nhập tin nhắn..."}
                  disabled={isTyping}
                  rows={1}
                  className="flex-1 resize-none bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none min-h-[24px] max-h-32 py-0.5 disabled:opacity-50"
                />
                <div className="flex gap-1 shrink-0">
                  <button className="p-1.5 rounded-md hover:bg-muted transition-colors" aria-label="Emoji">
                    <Smile className="w-4 h-4 text-muted-foreground" />
                  </button>
                  <button className="p-1.5 rounded-md hover:bg-muted transition-colors" aria-label="Voice">
                    <Mic className="w-4 h-4 text-muted-foreground" />
                  </button>
                  <button className="p-1.5 rounded-md hover:bg-muted transition-colors" aria-label="Regenerate">
                    <RotateCcw className="w-4 h-4 text-muted-foreground" />
                  </button>
                  <button
                    onClick={handleSend}
                    disabled={!input.trim() || isTyping}
                    className="p-2 rounded-md bg-foreground text-background hover:bg-foreground/90 disabled:opacity-30 transition-all"
                    aria-label="Send"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-[10px] text-muted-foreground text-center mt-2">
                VIDER có thể mắc lỗi. Hãy kiểm tra thông tin quan trọng.
              </p>
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <AnimatePresence>
          {rightOpen && (
            <motion.aside
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 280, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="hidden lg:flex flex-col border-l border-border bg-surface-sunken overflow-hidden shrink-0"
            >
              <div className="p-4 space-y-6 overflow-y-auto flex-1">
                {/* Quick prompts */}
                <div>
                  <p className="text-label text-muted-foreground mb-3">Gợi ý nhanh</p>
                  <div className="space-y-2">
                    {suggestedPrompts.map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => setInput(prompt)}
                        className="w-full text-left px-3 py-2.5 rounded-md border border-border bg-card text-sm hover:border-foreground/20 hover:vider-shadow transition-all duration-200 flex items-center gap-2"
                      >
                        <Sparkles className="w-3.5 h-3.5 text-vider-accent shrink-0" />
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>

                {/* System info */}
                <div>
                  <p className="text-label text-muted-foreground mb-3">Hệ thống</p>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Model</span>
                      <span className="font-medium">Qwen2.5-1.5B</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Trạng thái</span>
                      <span className="flex items-center gap-1.5">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            backendOnline ? "bg-green-500" : backendOnline === false ? "bg-red-500" : "bg-yellow-500"
                          }`}
                        />
                        {backendOnline ? "Online" : backendOnline === false ? "Offline" : "Checking…"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Backend</span>
                      <span className="font-medium text-xs font-mono">localhost:8000</span>
                    </div>
                  </div>
                </div>

                {/* Shortcuts */}
                <div>
                  <p className="text-label text-muted-foreground mb-3">Phím tắt</p>
                  <div className="space-y-2 text-xs text-muted-foreground">
                    <div className="flex justify-between">
                      <span>Gửi tin nhắn</span>
                      <kbd className="px-1.5 py-0.5 rounded border border-border bg-card font-mono">Enter</kbd>
                    </div>
                    <div className="flex justify-between">
                      <span>Xuống dòng</span>
                      <kbd className="px-1.5 py-0.5 rounded border border-border bg-card font-mono">Shift+Enter</kbd>
                    </div>
                    <div className="flex justify-between">
                      <span>Chat mới</span>
                      <kbd className="px-1.5 py-0.5 rounded border border-border bg-card font-mono">Ctrl+N</kbd>
                    </div>
                  </div>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
