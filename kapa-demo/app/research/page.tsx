"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Shell, PageHeader, Card, StatusBadge, Skeleton, ErrorBanner, tokens, ChevronRight } from "@/components/shared";

interface ResearchTask {
  id: string;
  issue_id: string;
  issue_title?: string;
  status: string;
  confidence_score?: number;
  created_at: string;
}

function SkeletonRows() {
  return (
    <>
      {[...Array(4)].map((_, i) => (
        <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
          {[...Array(5)].map((_, j) => (
            <td key={j} style={{ padding: "14px 16px" }}>
              <Skeleton h={12} w={j === 0 ? "55%" : j === 1 ? "45%" : j === 2 ? "25%" : j === 3 ? "20%" : "15%"} />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

function ConfidencePill({ score }: { score?: number }) {
  if (score == null) return <span style={{ color: "#444", fontSize: 12, fontFamily: tokens.font }}>—</span>;
  const pct = Math.round(score * 100);
  const color = pct >= 75 ? "#4ade80" : pct >= 45 ? "#fbbf24" : "#f87171";
  return (
    <span style={{
      fontSize: 12, fontWeight: 600, color,
      fontFamily: tokens.font, letterSpacing: "0.04em",
    }}>{pct}%</span>
  );
}

export default function ResearchPage() {
  const [tasks, setTasks] = useState<ResearchTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch all research — backend may return array directly or wrapped
    fetch("/api/research")
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(data => setTasks(Array.isArray(data) ? data : data.research ?? []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Shell>
      <PageHeader
        title="Research"
        subtitle="AI research tasks run against documentation sources for each issue."
      />
      <div style={{ padding: "28px 40px" }}>
        {error && <div style={{ marginBottom: 16 }}><ErrorBanner message={error} /></div>}
        <Card>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: tokens.font, fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
                  {["Research ID", "Issue", "Status", "Confidence", "Created", ""].map((h, i) => (
                    <th key={i} style={{ padding: "10px 16px", textAlign: "left", fontSize: 10, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: "#3a3a3a" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading && <SkeletonRows />}
                {!loading && tasks.length === 0 && !error && (
                  <tr><td colSpan={6} style={{ padding: "60px 16px", textAlign: "center", color: "#3a3a3a", fontFamily: tokens.font, fontSize: 13 }}>No research tasks found.</td></tr>
                )}
                {!loading && tasks.map(task => (
                  <tr
                    key={task.id}
                    style={{ borderBottom: "1px solid rgba(255,255,255,0.04)", transition: "background 0.12s" }}
                    onMouseEnter={e => (e.currentTarget.style.background = "rgba(255,255,255,0.02)")}
                    onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                  >
                    <td style={{ padding: "13px 16px", color: "#555", fontSize: 11, fontFamily: "'DM Mono', monospace" }}>
                      {task.id.slice(0, 12)}…
                    </td>
                    <td style={{ padding: "13px 16px" }}>
                      {task.issue_id ? (
                        <Link href={`/issues/${task.issue_id}`} style={{ color: tokens.textDim, textDecoration: "none" }}>
                          {task.issue_title ?? task.issue_id.slice(0, 10) + "…"}
                        </Link>
                      ) : "—"}
                    </td>
                    <td style={{ padding: "13px 16px" }}><StatusBadge status={task.status} /></td>
                    <td style={{ padding: "13px 16px" }}><ConfidencePill score={task.confidence_score} /></td>
                    <td style={{ padding: "13px 16px", color: "#555", fontSize: 12 }}>
                      {new Date(task.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                    </td>
                    <td style={{ padding: "13px 16px", textAlign: "right" }}>
                      <Link href={`/questions/${task.id}`} style={{
                        display: "inline-flex", alignItems: "center", gap: 4,
                        fontSize: 12, color: "#555", textDecoration: "none", transition: "color 0.15s",
                      }}
                        onMouseEnter={e => (e.currentTarget.style.color = "#a855f7")}
                        onMouseLeave={e => (e.currentTarget.style.color = "#555")}
                      >
                        Questions <ChevronRight />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </Shell>
  );
}
