"use client";
import { useState, useRef, useEffect } from "react";
import { Card, SendIcon, SparkleIcon, SpinIcon, Button, tokens } from "./shared";

interface Message {
  role: "user" | "assistant";
  content: string;
  ts: number;
}

interface FixChatPanelProps {
  readonly fixId: string;
  readonly fix: { id: string; issue_id: string; status: string; files: { file_path: string; diff?: string; markdown?: string }[] } | null;
  readonly onFixUpdated: (updated: { id: string; issue_id: string; status: string; files: { file_path: string; diff?: string; markdown?: string }[] }) => void;
  readonly onApprove: () => void;
  readonly apiBase?: string;
}

function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  return (
    <div style={{
      display: "flex", flexDirection: "column",
      alignItems: isUser ? "flex-end" : "flex-start",
      animation: "fadeUp 0.2s ease forwards",
    }}>
      {!isUser && (
        <div style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 5 }}>
          <div style={{
            width: 20, height: 20, borderRadius: 6,
            background: "linear-gradient(135deg,#a855f7,#7c3aed)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <SparkleIcon />
          </div>
          <span style={{ fontSize: 11, color: "#555", fontFamily: tokens.font }}>AI Assistant</span>
        </div>
      )}
      <div style={{
        maxWidth: "88%",
        padding: "9px 13px",
        borderRadius: isUser ? "10px 10px 3px 10px" : "3px 10px 10px 10px",
        background: isUser
          ? "linear-gradient(135deg,rgba(168,85,247,0.7),rgba(124,58,237,0.7))"
          : "rgba(255,255,255,0.05)",
        border: isUser ? "1px solid rgba(168,85,247,0.4)" : `1px solid ${tokens.border}`,
        color: isUser ? "#f0e8ff" : tokens.textDim,
        fontSize: 13, lineHeight: 1.65, fontFamily: tokens.font,
      }}>
        {msg.content}
      </div>
    </div>
  );
}

export function FixChatPanel(props: Readonly<FixChatPanelProps>) {
  const { fixId, fix, onFixUpdated, onApprove, apiBase = "" } = props;
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I've reviewed the proposed documentation fix. Feel free to ask me to revise specific sections, change the tone, add examples, or restructure any part of it.",
      ts: Date.now(),
    },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [approving, setApproving] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  const send = async () => {
    const text = input.trim();
    if (!text || thinking || !fixId) return;
    setInput("");
    const userMsg: Message = { role: "user", content: text, ts: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setThinking(true);
    try {
      const res = await fetch(`${apiBase}/api/fixes/${fixId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.files && fix) {
          onFixUpdated({ ...fix, files: data.files });
        }
        setMessages(prev => [...prev, { role: "assistant", content: "I've updated the proposed fix based on your request.", ts: Date.now() }]);
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: "Something went wrong updating the fix. Please try again.", ts: Date.now() }]);
      }
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Request failed. Please try again.", ts: Date.now() }]);
    }
    setThinking(false);
  };

  const handleApprove = async () => {
    if (approving || !fix) return;
    setApproving(true);
    try {
      const res = await fetch(`${apiBase}/api/fixes/${fixId}/approve`, { method: "POST", headers: { "Content-Type": "application/json" } });
      if (res.ok) onApprove();
    } finally {
      setApproving(false);
    }
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <Card style={{ display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
      {/* Header */}
      <div style={{
        padding: "14px 18px", borderBottom: `1px solid ${tokens.border}`,
        display: "flex", alignItems: "center", gap: 8, flexShrink: 0,
      }}>
        <div style={{
          width: 24, height: 24, borderRadius: 7,
          background: "linear-gradient(135deg,#a855f7,#7c3aed)",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <SparkleIcon />
        </div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: tokens.text, fontFamily: tokens.font }}>AI Assistant</div>
          <div style={{ fontSize: 11, color: "#555", fontFamily: tokens.font }}>Request edits to the proposed fix</div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
          {fix && fix.status !== "published" && fix.status !== "approved" && (
            <Button onClick={handleApprove} loading={approving} disabled={approving}>
              Approve
            </Button>
          )}
          <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#4ade80", fontFamily: tokens.font }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#4ade80" }} />
            Ready
          </div>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: "auto", padding: "16px 16px 8px", display: "flex", flexDirection: "column", gap: 14 }}>
        {messages.map((m) => <MessageBubble key={m.ts} msg={m} />)}
        {thinking && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, animation: "fadeUp 0.2s ease forwards" }}>
            <div style={{
              width: 20, height: 20, borderRadius: 6,
              background: "linear-gradient(135deg,#a855f7,#7c3aed)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <SparkleIcon />
            </div>
            <div style={{
              padding: "8px 12px", borderRadius: "3px 10px 10px 10px",
              background: "rgba(255,255,255,0.04)", border: `1px solid ${tokens.border}`,
              display: "flex", alignItems: "center", gap: 8,
            }}>
              <SpinIcon />
              <span style={{ fontSize: 12, color: "#555", fontFamily: tokens.font }}>Thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: "12px 14px", borderTop: `1px solid ${tokens.border}`,
        display: "flex", gap: 8, alignItems: "flex-end", flexShrink: 0,
      }}>
        <textarea
          rows={2}
          placeholder="Ask for a revision…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKey}
          style={{
            flex: 1, resize: "none",
            background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 8, padding: "9px 12px",
            color: tokens.text, fontSize: 13, fontFamily: tokens.font,
            outline: "none", lineHeight: 1.5,
          }}
          onFocus={e => (e.target.style.borderColor = "rgba(168,85,247,0.4)")}
          onBlur={e => (e.target.style.borderColor = "rgba(255,255,255,0.08)")}
        />
        <button
          onClick={send}
          disabled={!input.trim() || thinking || !fixId}
          style={{
            width: 36, height: 36, borderRadius: 8, border: "none", cursor: input.trim() && !thinking && fixId ? "pointer" : "default",
            background: input.trim() && !thinking && fixId ? "linear-gradient(135deg,#a855f7,#7c3aed)" : "rgba(255,255,255,0.05)",
            color: input.trim() && !thinking && fixId ? "#fff" : "#444",
            display: "flex", alignItems: "center", justifyContent: "center",
            transition: "all 0.15s", flexShrink: 0,
          }}
        >
          <SendIcon />
        </button>
      </div>
    </Card>
  );
}
