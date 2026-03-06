"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Shell, PageHeader, Card, StatusBadge, Skeleton, ErrorBanner, tokens, ChevronRight } from "@/components/shared";

interface Issue {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

function SkeletonRows() {
  return (
    <>
      {[...Array(5)].map((_, i) => (
        <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
          {[...Array(4)].map((_, j) => (
            <td key={j} style={{ padding: "14px 16px" }}>
              <Skeleton h={12} w={j === 0 ? "60%" : j === 1 ? "40%" : j === 2 ? "30%" : "20%"} />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

export default function IssuesPage() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/issues")
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(data => setIssues(Array.isArray(data) ? data : data.issues ?? []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Shell>
      <PageHeader
        title="Issues"
        subtitle="Documentation issues created from coverage gaps."
      />
      <div style={{ padding: "28px 40px" }}>
        {error && <div style={{ marginBottom: 16 }}><ErrorBanner message={error} /></div>}
        <Card>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: tokens.font, fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
                  {["Title", "Status", "Created", ""].map((h, i) => (
                    <th key={i} style={{ padding: "10px 16px", textAlign: "left", fontSize: 10, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: "#3a3a3a" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading && <SkeletonRows />}
                {!loading && issues.length === 0 && !error && (
                  <tr><td colSpan={4} style={{ padding: "60px 16px", textAlign: "center", color: "#3a3a3a", fontFamily: tokens.font, fontSize: 13 }}>No issues found.</td></tr>
                )}
                {!loading && issues.map(issue => (
                  <tr
                    key={issue.id}
                    style={{ borderBottom: "1px solid rgba(255,255,255,0.04)", transition: "background 0.12s" }}
                    onMouseEnter={e => (e.currentTarget.style.background = "rgba(255,255,255,0.02)")}
                    onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                  >
                    <td style={{ padding: "13px 16px" }}>
                      <Link href={`/issues/${issue.id}`} style={{ color: tokens.text, textDecoration: "none", fontWeight: 500 }}>
                        {issue.title}
                      </Link>
                    </td>
                    <td style={{ padding: "13px 16px" }}>
                      <StatusBadge status={issue.status} />
                    </td>
                    <td style={{ padding: "13px 16px", color: "#555", fontSize: 12 }}>
                      {new Date(issue.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                    </td>
                    <td style={{ padding: "13px 16px", textAlign: "right" }}>
                      <Link href={`/issues/${issue.id}`} style={{
                        display: "inline-flex", alignItems: "center", gap: 4,
                        fontSize: 12, color: "#555", textDecoration: "none", transition: "color 0.15s",
                      }}
                        onMouseEnter={e => (e.currentTarget.style.color = "#a855f7")}
                        onMouseLeave={e => (e.currentTarget.style.color = "#555")}
                      >
                        View <ChevronRight />
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
