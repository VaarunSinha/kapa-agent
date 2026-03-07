"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

// ─── Icons ────────────────────────────────────────────────────────────────────
const IconDashboard = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
    <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
  </svg>
);
const IconConversations = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
  </svg>
);
const IconUsers = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
    <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
  </svg>
);
const IconGaps = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35M11 8v3M11 14h.01"/>
  </svg>
);
const IconIssues = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);
const IconResearch = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/>
  </svg>
);
const IconFixes = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
  </svg>
);
const IconAnalytics = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
    <line x1="6" y1="20" x2="6" y2="14"/>
  </svg>
);
const IconSources = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
  </svg>
);
const IconIntegrations = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
    <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
  </svg>
);
const IconKeys = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
  </svg>
);
const IconChat = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
    <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
  </svg>
);
const IconGithub = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
  </svg>
);
const IconSparkle = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>
  </svg>
);
const IconSearch = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
  </svg>
);
const IconLoader = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="animate-spin">
    <path d="M21 12a9 9 0 11-6.219-8.56"/>
  </svg>
);
const IconZap = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
  </svg>
);
const IconCheck = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);
const IconChevronRight = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="9 18 15 12 9 6"/>
  </svg>
);

// ─── Sidebar ──────────────────────────────────────────────────────────────────
const navGroups = [
  {
    label: null,
    items: [{ id: "dashboard", label: "Dashboard", icon: IconDashboard }],
  },
  {
    label: "ANALYTICS",
    items: [
      { id: "conversations", label: "Conversations", icon: IconConversations },
      { id: "users", label: "Users", icon: IconUsers },
      { id: "coverage-gaps", label: "Coverage Gaps", icon: IconGaps, badge: "NEW", active: true },
      { id: "source-analytics", label: "Source Analytics", icon: IconAnalytics },
    ],
  },
  {
    label: "WORKFLOW",
    items: [
      { id: "issues", label: "Issues", icon: IconIssues, href: "/issues" },
      { id: "research", label: "Research", icon: IconResearch, href: "/research" },
      { id: "fixes", label: "Fixes", icon: IconFixes, href: "/fixes" },
    ],
  },
  {
    label: "CONFIGURATION",
    items: [
      { id: "sources", label: "Sources", icon: IconSources },
      { id: "integrations", label: "Integrations", icon: IconIntegrations },
      { id: "api-keys", label: "API Keys", icon: IconKeys },
    ],
  },
  {
    label: "PLAYGROUND",
    items: [{ id: "chat", label: "Chat", icon: IconChat }],
  },
];

function Sidebar() {
  return (
    <aside
      style={{
        width: 220,
        minWidth: 220,
        background: "#0e0e10",
        borderRight: "1px solid rgba(255,255,255,0.06)",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        position: "sticky",
        top: 0,
        fontFamily: "'DM Mono', 'Fira Code', monospace",
      }}
    >
      {/* Logo - link to home */}
      <div style={{ padding: "18px 18px 14px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <Link href="/" style={{ textDecoration: "none", color: "inherit" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
            <div style={{
              width: 28, height: 28, borderRadius: 8,
              background: "linear-gradient(135deg,#a855f7,#7c3aed)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 13, fontWeight: 700, color: "#fff",
            }}>k</div>
            <span style={{ fontSize: 14, fontWeight: 600, color: "#f0f0f0", letterSpacing: "0.02em" }}>kapa.ai</span>
            <span style={{
              fontSize: 9, fontWeight: 700, letterSpacing: "0.1em",
              background: "rgba(168,85,247,0.18)", color: "#a855f7",
              border: "1px solid rgba(168,85,247,0.3)", borderRadius: 4,
              padding: "2px 5px",
            }}>KAPA</span>
          </div>
        </Link>
      </div>

      {/* Project selector */}
      <div style={{ padding: "10px 12px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "6px 10px", borderRadius: 6,
          background: "rgba(255,255,255,0.04)", cursor: "pointer",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              width: 20, height: 20, borderRadius: 5,
              background: "linear-gradient(135deg,#7c3aed,#4f46e5)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 10, color: "#fff", fontWeight: 700,
            }}>A</div>
            <span style={{ fontSize: 12, color: "#c0c0c0" }}>Ask AI (External)</span>
          </div>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
        {navGroups.map((group, gi) => (
          <div key={gi}>
            {group.label && (
              <div style={{
                padding: "14px 18px 4px",
                fontSize: 10, fontWeight: 600, letterSpacing: "0.12em",
                color: "#444", textTransform: "uppercase",
              }}>{group.label}</div>
            )}
            {group.items.map((item) => {
              const Icon = item.icon;
              const isLink = !!item.href;
              const style = {
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "7px 18px",
                cursor: "pointer", borderRadius: 0,
                background: item.active ? "rgba(168,85,247,0.12)" : "transparent",
                borderLeft: item.active ? "2px solid #a855f7" : "2px solid transparent",
                color: item.active ? "#c084fc" : "#6b6b6b",
                transition: "all 0.15s",
                textDecoration: "none",
              };
              const content = (
                <>
                  <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                    <Icon />
                    <span style={{ fontSize: 13 }}>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span style={{
                      fontSize: 9, fontWeight: 700, letterSpacing: "0.08em",
                      background: "rgba(168,85,247,0.2)", color: "#a855f7",
                      border: "1px solid rgba(168,85,247,0.3)",
                      borderRadius: 4, padding: "2px 5px",
                    }}>{item.badge}</span>
                  )}
                </>
              );
              if (isLink) {
                return (
                  <Link
                    key={item.id}
                    href={item.href}
                    style={style}
                  >
                    {content}
                  </Link>
                );
              }
              return (
                <div key={item.id} style={style}>
                  {content}
                </div>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User */}
      <div style={{
        padding: "12px 18px", borderTop: "1px solid rgba(255,255,255,0.06)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 26, height: 26, borderRadius: "50%",
            background: "linear-gradient(135deg,#7c3aed,#a855f7)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 11, color: "#fff", fontWeight: 700,
          }}>D</div>
          <span style={{ fontSize: 11, color: "#666" }}>david@kapa.ai</span>
        </div>
      </div>
    </aside>
  );
}

// API base URL for Django backend (e.g. http://localhost:8000). Leave empty if same origin or proxied.
const API_BASE = typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL
  ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
  : "";

// ─── Status Badge ─────────────────────────────────────────────────────────────
const STATUS_CONFIG = {
  open: { label: "Open", bg: "rgba(59,130,246,0.15)", color: "#60a5fa", border: "rgba(59,130,246,0.3)" },
  to_review: { label: "To Review", bg: "rgba(234,179,8,0.15)", color: "#fbbf24", border: "rgba(234,179,8,0.3)" },
  resolved: { label: "Resolved", bg: "rgba(34,197,94,0.15)", color: "#4ade80", border: "rgba(34,197,94,0.3)" },
  acted: { label: "Acted", bg: "rgba(168,85,247,0.15)", color: "#c084fc", border: "rgba(168,85,247,0.3)" },
};

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.open;
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, letterSpacing: "0.06em",
      background: cfg.bg, color: cfg.color,
      border: `1px solid ${cfg.border}`,
      borderRadius: 5, padding: "3px 9px",
      textTransform: "uppercase",
      fontFamily: "'DM Mono', monospace",
    }}>{cfg.label}</span>
  );
}

// ─── CoverageGapCard ──────────────────────────────────────────────────────────
function CoverageGapCard({ gap, onAct }) {
  const router = useRouter();
  const [acting, setActing] = useState(false);
  const [localStatus, setLocalStatus] = useState(gap.status);

  const handleAct = async () => {
    setActing(true);
    try {
      const data = await onAct(gap.id);
      setLocalStatus("acted");
      if (data?.issue_id) {
        setTimeout(() => router.push(`/issues/${data.issue_id}`), 600);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setActing(false);
    }
  };

  return (
    <div style={{
      background: "#111113",
      border: "1px solid rgba(255,255,255,0.07)",
      borderRadius: 12,
      overflow: "hidden",
      transition: "border-color 0.2s",
    }}
      onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(168,85,247,0.25)"}
      onMouseLeave={e => e.currentTarget.style.borderColor = "rgba(255,255,255,0.07)"}
    >
      {/* Card header */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "14px 18px",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        background: "rgba(255,255,255,0.02)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{
            fontSize: 14, fontWeight: 600, color: "#e8e8e8",
            fontFamily: "'DM Mono', monospace",
          }}>{gap.title}</span>
          <span style={{
            fontSize: 11, color: "#555", fontFamily: "'DM Mono', monospace",
            background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 5, padding: "2px 8px",
          }}>{gap.conversationCount} conversations</span>
        </div>
        <StatusBadge status={localStatus} />
      </div>

      {/* Card body */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 0 }}>
        {/* Finding */}
        <div style={{
          padding: "16px 18px",
          borderRight: "1px solid rgba(255,255,255,0.06)",
        }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 6, marginBottom: 10,
            color: "#888",
          }}>
            <IconSearch />
            <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", fontFamily: "'DM Mono', monospace" }}>Finding</span>
          </div>
          <p style={{ fontSize: 13, color: "#9a9a9a", lineHeight: 1.65, margin: 0, fontFamily: "'DM Mono', monospace" }}>
            {gap.finding}
          </p>
        </div>

        {/* Suggestion */}
        <div style={{
          padding: "16px 18px",
          background: "rgba(168,85,247,0.04)",
        }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 6, marginBottom: 10,
            color: "#a855f7",
          }}>
            <IconSparkle />
            <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", fontFamily: "'DM Mono', monospace" }}>Suggestion</span>
          </div>
          <p style={{ fontSize: 13, color: "#c4a8e8", lineHeight: 1.65, margin: 0, fontFamily: "'DM Mono', monospace" }}>
            {gap.suggestion}
          </p>
        </div>
      </div>

      {/* Card footer / actions */}
      <div style={{
        padding: "12px 18px",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        display: "flex", alignItems: "center", gap: 10,
        background: "rgba(255,255,255,0.015)",
      }}>
        {/* Act */}
        <button
          onClick={handleAct}
          disabled={acting || localStatus === "acted"}
          style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            padding: "7px 16px", borderRadius: 7,
            background: localStatus === "acted"
              ? "rgba(168,85,247,0.12)"
              : "linear-gradient(135deg,rgba(168,85,247,0.8),rgba(124,58,237,0.8))",
            border: localStatus === "acted"
              ? "1px solid rgba(168,85,247,0.3)"
              : "1px solid rgba(168,85,247,0.5)",
            color: localStatus === "acted" ? "#a855f7" : "#fff",
            fontSize: 12, fontWeight: 600, cursor: acting || localStatus === "acted" ? "default" : "pointer",
            fontFamily: "'DM Mono', monospace",
            opacity: acting ? 0.7 : 1,
            transition: "all 0.15s",
            outline: "none",
          }}
          onMouseEnter={e => { if (localStatus !== "acted" && !acting) e.currentTarget.style.filter = "brightness(1.15)"; }}
          onMouseLeave={e => { e.currentTarget.style.filter = "none"; }}
        >
          {acting ? <IconLoader /> : localStatus === "acted" ? <IconCheck /> : <IconZap />}
          {acting ? "Working…" : localStatus === "acted" ? "Acted" : "Act"}
        </button>
      </div>
    </div>
  );
}

// ─── MetricsPanel ─────────────────────────────────────────────────────────────
function MetricsPanel({ conversationsProcessed, coverageGapsIdentified }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 28 }}>
      {[
        { label: "Conversations Processed", value: conversationsProcessed },
        { label: "Coverage Gaps Identified", value: coverageGapsIdentified },
      ].map((m) => (
        <div
          key={m.label}
          style={{
            background: "#111113",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: 12,
            padding: "22px 26px",
          }}
        >
          <div style={{ fontSize: 12, color: "#555", marginBottom: 8, fontFamily: "'DM Mono', monospace", letterSpacing: "0.04em" }}>
            {m.label}
          </div>
          <div style={{ fontSize: 38, fontWeight: 700, color: "#f0f0f0", letterSpacing: "-0.02em", fontFamily: "'DM Mono', monospace" }}>
            {m.value ?? "—"}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ w = "100%", h = 16, radius = 6 }) {
  return (
    <div style={{
      width: w, height: h, borderRadius: radius,
      background: "linear-gradient(90deg,#1a1a1c 25%,#222224 50%,#1a1a1c 75%)",
      backgroundSize: "200% 100%",
      animation: "shimmer 1.4s infinite",
    }} />
  );
}

// ─── Empty State ──────────────────────────────────────────────────────────────
function EmptyState() {
  return (
    <div style={{
      textAlign: "center", padding: "80px 0",
      color: "#444", fontFamily: "'DM Mono', monospace",
    }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🎉</div>
      <div style={{ fontSize: 16, fontWeight: 600, color: "#888", marginBottom: 8 }}>No coverage gaps found</div>
      <div style={{ fontSize: 13, color: "#444" }}>Your documentation is fully covering all user queries.</div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function CoverageGapsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/coverage-gaps`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        setData(json);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAct = useCallback(async (id) => {
    const res = await fetch(`${API_BASE}/api/coverage-gaps/${id}/act`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }, []);

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#0a0a0c" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
        @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
        @keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        .gap-card-enter { animation: fadeIn 0.35s ease forwards; }
      `}</style>

      <Sidebar />

      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "auto" }}>
        {/* Top bar */}
        <div style={{
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          padding: "14px 32px",
          display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 10,
          background: "rgba(0,0,0,0.4)", backdropFilter: "blur(8px)",
          position: "sticky", top: 0, zIndex: 10,
        }}>
          {data?.hasConnectedRepo && data?.connectedRepo && (
            <Link
              href={`/github/setup?installation_id=${data.connectedRepo.installation_id}`}
              style={{
                display: "inline-flex", alignItems: "center", gap: 6,
                padding: "7px 14px", borderRadius: 8,
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                color: "#c0c0c0", textDecoration: "none",
                fontSize: 13, fontWeight: 500, fontFamily: "'DM Mono', monospace",
                transition: "all 0.15s",
              }}
              onMouseEnter={e => { e.currentTarget.style.background = "rgba(255,255,255,0.09)"; e.currentTarget.style.color = "#fff"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.05)"; e.currentTarget.style.color = "#c0c0c0"; }}
            >
              <IconGithub />
              Connected: {data.connectedRepo.owner}/{data.connectedRepo.repository_name}
              <IconChevronRight />
            </Link>
          )}
          {data?.githubInstallUrl && !data?.hasConnectedRepo && (
            <a
              href={data.githubInstallUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "inline-flex", alignItems: "center", gap: 6,
                padding: "7px 14px", borderRadius: 8,
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                color: "#c0c0c0", textDecoration: "none",
                fontSize: 13, fontWeight: 500, fontFamily: "'DM Mono', monospace",
                transition: "all 0.15s",
              }}
              onMouseEnter={e => { e.currentTarget.style.background = "rgba(255,255,255,0.09)"; e.currentTarget.style.color = "#fff"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "rgba(255,255,255,0.05)"; e.currentTarget.style.color = "#c0c0c0"; }}
            >
              <IconGithub />
              Connect Source Code
              <IconChevronRight />
            </a>
          )}
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            padding: "7px 16px", borderRadius: 8,
            background: "linear-gradient(135deg,rgba(168,85,247,0.9),rgba(124,58,237,0.9))",
            color: "#fff", fontSize: 13, fontWeight: 600,
            cursor: "pointer", fontFamily: "'DM Mono', monospace",
          }}>
            <IconSparkle />
            Ask AI
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: "36px 40px", maxWidth: 1200, width: "100%" }}>
          {/* Page title */}
          <div style={{ marginBottom: 8 }}>
            <h1 style={{
              fontSize: 28, fontWeight: 700, color: "#f0f0f0", margin: 0,
              fontFamily: "'DM Mono', monospace", letterSpacing: "-0.02em",
            }}>Coverage Gaps</h1>
          </div>
          <p style={{
            fontSize: 13, color: "#555", marginBottom: 32,
            fontFamily: "'DM Mono', monospace", lineHeight: 1.6,
          }}>
            Identify content and product gaps where your AI assistant struggles to provide complete answers.{" "}
            <a href="#" style={{ color: "#7c3aed", textDecoration: "none" }}>Learn more →</a>
          </p>

          {/* Loading skeleton */}
          {loading && (
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 12 }}>
                {[0, 1].map(i => (
                  <div key={i} style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 12, padding: "22px 26px" }}>
                    <Skeleton w="60%" h={12} />
                    <div style={{ marginTop: 12 }}><Skeleton w="40%" h={36} /></div>
                  </div>
                ))}
              </div>
              {[0, 1, 2].map(i => (
                <div key={i} style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 12, padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
                  <Skeleton w="35%" h={16} />
                  <Skeleton w="100%" h={12} />
                  <Skeleton w="80%" h={12} />
                </div>
              ))}
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{
              background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
              borderRadius: 10, padding: "16px 20px", color: "#f87171",
              fontSize: 13, fontFamily: "'DM Mono', monospace",
            }}>
              ⚠ Failed to load coverage gaps: {error}
            </div>
          )}

          {/* Data */}
          {!loading && !error && data && (
            <>
              <MetricsPanel
                conversationsProcessed={data.conversationsProcessed}
                coverageGapsIdentified={data.coverageGapsIdentified}
              />

              {data.gaps && data.gaps.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  {data.gaps.map((gap, i) => (
                    <div
                      key={gap.id}
                      className="gap-card-enter"
                      style={{ animationDelay: `${i * 0.07}s`, opacity: 0 }}
                    >
                      <CoverageGapCard
                        gap={gap}
                        onAct={handleAct}
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState />
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
