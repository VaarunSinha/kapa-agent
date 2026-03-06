"use client";
import { useState, useRef, useEffect } from "react";
import { Card, SendIcon, SparkleIcon, SpinIcon, tokens } from "./shared";

interface Message {
  role: "user" | "assistant";
  content: string;
  ts: number;
}

const PLACEHOLDER_RESPONSES = [
  "I'll update the proposed fix to reflect that change. Give me a moment to revise the documentation structure.",
  "Good point. I can add a more detailed code example to that section — would you like me to include TypeScript types as well?",
  "Understood. I'll simplify the language in that paragraph and make it more accessible for developers new to this concept.",
  "I've noted the feedback. The fix will be updated to include the additional edge case you mentioned.",
  "Sure — I can restructure that section to use a step-by-step format instead of a prose explanation.",
  "I'll add the missing configuration options to the reference table in the proposed documentation.",
];

let placeholderIdx = 0;
function getPlaceholder() {
  const r = PLACEHOLDER_RESPONSES[placeholderIdx % PLACEHOLDER_RESPONSES.length];
  placeholderIdx++;
  return r;
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

export function FixChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I've reviewed the proposed documentation fix. Feel free to ask me to revise specific sections, change the tone, add examples, or restructure any part of it.",
      ts: Date.now(),
    },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  const send = async () => {
    const text = input.trim();
    if (!text || thinking) return;
    setInput("");
    const userMsg: Message = { role: "user", content: text, ts: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setThinking(true);
    await new Promise(r => setTimeout(r, 900 + Math.random() * 600));
    const aiMsg: Message = { role: "assistant", content: getPlaceholder(), ts: Date.now() };
    setMessages(prev => [...prev, aiMsg]);
    setThinking(false);
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
        <div style={{
          marginLeft: "auto", display: "flex", alignItems: "center", gap: 5,
          fontSize: 11, color: "#4ade80", fontFamily: tokens.font,
        }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#4ade80" }} />
          Ready
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
          disabled={!input.trim() || thinking}
          style={{
            width: 36, height: 36, borderRadius: 8, border: "none", cursor: input.trim() && !thinking ? "pointer" : "default",
            background: input.trim() && !thinking ? "linear-gradient(135deg,#a855f7,#7c3aed)" : "rgba(255,255,255,0.05)",
            color: input.trim() && !thinking ? "#fff" : "#444",
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
