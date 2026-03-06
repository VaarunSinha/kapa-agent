"use client";
import type { ReactElement } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

// ─── Design tokens ────────────────────────────────────────────────────────────
export const tokens = {
  bg: "#09090b",
  surface: "#111113",
  surfaceHover: "#18181b",
  border: "rgba(255,255,255,0.07)",
  borderHover: "rgba(168,85,247,0.3)",
  purple: "#a855f7",
  purpleDim: "rgba(168,85,247,0.15)",
  purpleBorder: "rgba(168,85,247,0.3)",
  text: "#f0f0f0",
  textMuted: "#6b6b6b",
  textDim: "#9a9a9a",
  font: "'DM Mono', 'Fira Code', monospace",
};

// ─── Status config ────────────────────────────────────────────────────────────
export const STATUS_MAP: Record<string, { label: string; color: string; bg: string; border: string }> = {
  open:        { label: "Open",        color: "#60a5fa", bg: "rgba(59,130,246,0.12)",  border: "rgba(59,130,246,0.3)"  },
  "to-review": { label: "To Review",   color: "#fbbf24", bg: "rgba(234,179,8,0.12)",   border: "rgba(234,179,8,0.3)"   },
  in_progress: { label: "In Progress", color: "#fb923c", bg: "rgba(251,146,60,0.12)",  border: "rgba(251,146,60,0.3)"  },
  resolved:    { label: "Resolved",    color: "#4ade80", bg: "rgba(34,197,94,0.12)",   border: "rgba(34,197,94,0.3)"   },
  acted:       { label: "Acted",       color: "#c084fc", bg: "rgba(168,85,247,0.12)",  border: "rgba(168,85,247,0.3)"  },
  pending:     { label: "Pending",     color: "#94a3b8", bg: "rgba(148,163,184,0.12)", border: "rgba(148,163,184,0.3)" },
  complete:    { label: "Complete",    color: "#4ade80", bg: "rgba(34,197,94,0.12)",   border: "rgba(34,197,94,0.3)"   },
  draft:       { label: "Draft",       color: "#fb923c", bg: "rgba(251,146,60,0.12)",  border: "rgba(251,146,60,0.3)"  },
};

export function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_MAP[status] ?? STATUS_MAP["pending"];
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, letterSpacing: "0.06em",
      background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}`,
      borderRadius: 5, padding: "3px 9px", textTransform: "uppercase",
      fontFamily: tokens.font, whiteSpace: "nowrap",
    }}>{cfg.label}</span>
  );
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────
export function Skeleton({ w = "100%", h = 14, radius = 6 }: { w?: string | number; h?: number; radius?: number }) {
  return (
    <div style={{
      width: w, height: h, borderRadius: radius,
      background: "linear-gradient(90deg,#1a1a1c 25%,#232325 50%,#1a1a1c 75%)",
      backgroundSize: "200% 100%",
      animation: "shimmer 1.5s infinite",
    }} />
  );
}

// ─── Error banner ─────────────────────────────────────────────────────────────
export function ErrorBanner({ message }: { message: string }) {
  return (
    <div style={{
      background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
      borderRadius: 10, padding: "14px 18px", color: "#f87171",
      fontSize: 13, fontFamily: tokens.font,
    }}>⚠ {message}</div>
  );
}

// ─── Button ───────────────────────────────────────────────────────────────────
export function Button({
  children, onClick, variant = "primary", disabled = false, loading = false, as: As,
  href, style: extraStyle,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  disabled?: boolean;
  loading?: boolean;
  as?: any;
  href?: string;
  style?: React.CSSProperties;
}) {
  const base: React.CSSProperties = {
    display: "inline-flex", alignItems: "center", gap: 7,
    padding: "8px 16px", borderRadius: 8,
    fontSize: 12, fontWeight: 600, cursor: disabled || loading ? "default" : "pointer",
    fontFamily: tokens.font, border: "1px solid transparent",
    opacity: disabled || loading ? 0.6 : 1, transition: "all 0.15s",
    outline: "none", textDecoration: "none",
    ...extraStyle,
  };
  const variants = {
    primary: { background: "linear-gradient(135deg,rgba(168,85,247,0.9),rgba(124,58,237,0.9))", color: "#fff", borderColor: "rgba(168,85,247,0.5)" },
    secondary: { background: "rgba(255,255,255,0.05)", color: "#c0c0c0", borderColor: "rgba(255,255,255,0.1)" },
    ghost: { background: "transparent", color: "#6b6b6b", borderColor: "rgba(255,255,255,0.06)" },
  };
  const s = { ...base, ...variants[variant] };
  if (As === "a" && href) return <a href={href} style={s}>{children}</a>;
  return <button style={s} onClick={onClick} disabled={disabled || loading}>{loading ? <SpinIcon /> : null}{children}</button>;
}

// ─── Icons ────────────────────────────────────────────────────────────────────
export const SpinIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ animation: "spin 0.8s linear infinite" }}><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
);
export const ChevronRight = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"/></svg>
);
export const ArrowLeft = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
);
export const SendIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
);
export const FileIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
);
export const BrainIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.96-.46 2.5 2.5 0 01-1.07-4.73A3 3 0 016.5 9a2.5 2.5 0 010-5A2.5 2.5 0 019.5 2z"/><path d="M14.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 004.96-.46 2.5 2.5 0 001.07-4.73A3 3 0 0017.5 9a2.5 2.5 0 000-5A2.5 2.5 0 0014.5 2z"/></svg>
);
export const CheckIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
);
export const SparkleIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/></svg>
);

// ─── Sidebar nav ──────────────────────────────────────────────────────────────
const NAV = [
  { group: null,           items: [{ id: "dashboard",      href: "/",               label: "Dashboard" }] },
  { group: "ANALYTICS",    items: [
    { id: "conversations", href: "/conversations",          label: "Conversations" },
    { id: "users",         href: "/users",                  label: "Users" },
    { id: "coverage-gaps", href: "/dashboard",              label: "Coverage Gaps", badge: "NEW" },
    { id: "source-analytics", href: "/source-analytics",   label: "Source Analytics" },
  ]},
  { group: "WORKFLOW",     items: [
    { id: "issues",        href: "/issues",                 label: "Issues" },
    { id: "research",      href: "/research",               label: "Research" },
    { id: "fixes",         href: "/fixes",                  label: "Fixes" },
  ]},
  { group: "CONFIGURATION", items: [
    { id: "sources",       href: "/sources",                label: "Sources" },
    { id: "integrations",  href: "/integrations",           label: "Integrations" },
    { id: "api-keys",      href: "/api-keys",               label: "API Keys" },
  ]},
  { group: "PLAYGROUND",   items: [{ id: "chat", href: "/chat", label: "Chat" }] },
];

const NAV_ICONS: Record<string, () => ReactElement> = {
  dashboard: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>,
  conversations: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>,
  users: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>,
  "coverage-gaps": () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35M11 8v3M11 14h.01"/></svg>,
  "source-analytics": () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,
  issues: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  research: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>,
  fixes: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>,
  sources: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>,
  integrations: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>,
  "api-keys": () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>,
  chat: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>,
};

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside style={{
      width: 220, minWidth: 220,
      background: "#0e0e10",
      borderRight: `1px solid ${tokens.border}`,
      display: "flex", flexDirection: "column",
      height: "100vh", position: "sticky", top: 0,
      fontFamily: tokens.font,
    }}>
      {/* Logo */}
      <div style={{ padding: "18px 18px 14px", borderBottom: `1px solid ${tokens.border}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: "linear-gradient(135deg,#a855f7,#7c3aed)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, color: "#fff" }}>k</div>
          <span style={{ fontSize: 14, fontWeight: 600, color: "#f0f0f0", letterSpacing: "0.02em" }}>kapa.ai</span>
          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.1em", background: "rgba(168,85,247,0.18)", color: "#a855f7", border: "1px solid rgba(168,85,247,0.3)", borderRadius: 4, padding: "2px 5px" }}>KAPA</span>
        </div>
      </div>
      {/* Project */}
      <div style={{ padding: "10px 12px", borderBottom: `1px solid ${tokens.border}` }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 10px", borderRadius: 6, background: "rgba(255,255,255,0.04)", cursor: "pointer" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 20, height: 20, borderRadius: 5, background: "linear-gradient(135deg,#7c3aed,#4f46e5)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "#fff", fontWeight: 700 }}>A</div>
            <span style={{ fontSize: 12, color: "#c0c0c0" }}>Ask AI (External)</span>
          </div>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#555" strokeWidth="2"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
      </div>
      {/* Nav */}
      <nav style={{ flex: 1, overflowY: "auto", padding: "6px 0" }}>
        {NAV.map((group, gi) => (
          <div key={gi}>
            {group.group && (
              <div style={{ padding: "12px 18px 4px", fontSize: 10, fontWeight: 600, letterSpacing: "0.12em", color: "#3a3a3a", textTransform: "uppercase" }}>{group.group}</div>
            )}
            {group.items.map((item) => {
              const Icon = NAV_ICONS[item.id];
              const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link key={item.id} href={item.href} style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "7px 18px", textDecoration: "none",
                  background: active ? "rgba(168,85,247,0.1)" : "transparent",
                  borderLeft: active ? "2px solid #a855f7" : "2px solid transparent",
                  color: active ? "#c084fc" : "#555",
                  transition: "all 0.12s",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                    {Icon && <Icon />}
                    <span style={{ fontSize: 13 }}>{item.label}</span>
                  </div>
                  {(item as any).badge && (
                    <span style={{ fontSize: 9, fontWeight: 700, background: "rgba(168,85,247,0.2)", color: "#a855f7", border: "1px solid rgba(168,85,247,0.3)", borderRadius: 4, padding: "2px 5px" }}>{(item as any).badge}</span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
      {/* User */}
      <div style={{ padding: "12px 18px", borderTop: `1px solid ${tokens.border}`, display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ width: 26, height: 26, borderRadius: "50%", background: "linear-gradient(135deg,#7c3aed,#a855f7)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, color: "#fff", fontWeight: 700 }}>D</div>
        <span style={{ fontSize: 11, color: "#555", fontFamily: tokens.font }}>david@kapa.ai</span>
      </div>
    </aside>
  );
}

// ─── Shell ────────────────────────────────────────────────────────────────────
export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: tokens.bg }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap');
        *{box-sizing:border-box;margin:0;padding:0}
        ::-webkit-scrollbar{width:4px;height:4px}
        ::-webkit-scrollbar-track{background:transparent}
        ::-webkit-scrollbar-thumb{background:#2a2a2c;border-radius:4px}
        @keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        @keyframes slideIn{from{opacity:0;transform:translateX(12px)}to{opacity:1;transform:translateX(0)}}
        a{color:inherit}
      `}</style>
      <Sidebar />
      <main style={{ flex: 1, overflow: "auto", fontFamily: tokens.font }}>
        {children}
      </main>
    </div>
  );
}

// ─── Page header ──────────────────────────────────────────────────────────────
export function PageHeader({ title, subtitle, back, children }: {
  title: string; subtitle?: string; back?: { href: string; label: string }; children?: React.ReactNode;
}) {
  return (
    <div style={{ padding: "32px 40px 24px", borderBottom: `1px solid ${tokens.border}` }}>
      {back && (
        <Link href={back.href} style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, color: "#555", textDecoration: "none", marginBottom: 14, transition: "color 0.15s" }}>
          <ArrowLeft /> {back.label}
        </Link>
      )}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 700, color: tokens.text, letterSpacing: "-0.02em" }}>{title}</h1>
          {subtitle && <p style={{ fontSize: 13, color: tokens.textMuted, marginTop: 5, lineHeight: 1.6 }}>{subtitle}</p>}
        </div>
        {children && <div style={{ display: "flex", gap: 10, alignItems: "center" }}>{children}</div>}
      </div>
    </div>
  );
}

// ─── Card ─────────────────────────────────────────────────────────────────────
export function Card({ children, style: s }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={{ background: tokens.surface, border: `1px solid ${tokens.border}`, borderRadius: 12, ...s }}>
      {children}
    </div>
  );
}

// ─── Section label ────────────────────────────────────────────────────────────
export function SectionLabel({ icon, label }: { icon?: React.ReactNode; label: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 14 }}>
      {icon && <span style={{ color: "#a855f7" }}>{icon}</span>}
      <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: "#555" }}>{label}</span>
    </div>
  );
}

// ─── Table ────────────────────────────────────────────────────────────────────
export function Table({ cols, rows }: {
  cols: string[];
  rows: React.ReactNode[][];
}) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: tokens.font, fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: `1px solid ${tokens.border}` }}>
            {cols.map((c, i) => (
              <th key={i} style={{ padding: "10px 16px", textAlign: "left", fontSize: 10, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: "#444" }}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} style={{ borderBottom: `1px solid rgba(255,255,255,0.04)`, transition: "background 0.12s" }}
              onMouseEnter={e => (e.currentTarget.style.background = "rgba(255,255,255,0.02)")}
              onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
            >
              {row.map((cell, ci) => (
                <td key={ci} style={{ padding: "12px 16px", color: tokens.textDim }}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function EmptyTableRow({ cols, message }: { cols: number; message: string }) {
  return (
    <tr>
      <td colSpan={cols} style={{ padding: "60px 16px", textAlign: "center", color: "#444", fontFamily: tokens.font, fontSize: 13 }}>
        {message}
      </td>
    </tr>
  );
}
