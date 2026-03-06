"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Shell, PageHeader, Card, StatusBadge, Skeleton, ErrorBanner, tokens, ChevronRight } from "@/components/shared";

interface Fix {
  id: string;
  issue_id: string;
  issue_title?: string;
  status: string;
  files_count?: number;
  created_at: string;
}

function SkeletonRows() {
  return (
    <>
      {[...Array(4)].map((_, i) => (
        <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
          {[...Array(5)].map((_, j) => (
            <td key={j} style={{ padding: "14px 16px" }}>
              <Skeleton h={12} w={j === 0 ? "45%" : j === 1 ? "50%" : j === 2 ? "25%" : j === 3 ? "20%" : "15%"} />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

export default function FixesPage() {
  const [fixes, setFixes] = useState<Fix[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/fixes")
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(data => setFixes(Array.isArray(data) ? data : data.fixes ?? []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Shell>
      <PageHeader
        title="Fixes"
        subtitle="AI-generated documentation fixes ready for review."
      />
      <div style={{ padding: "28px 40px" }}>
        {error && <div style={{ marginBottom: 16 }}><ErrorBanner message={error} /></div>}
        <Card>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: tokens.font, fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
                  {["Fix ID", "Issue", "Status", "Files", "Created", ""].map((h, i) => (
                    <th key={i} style={{ padding: "10px 16px", textAlign: "left", fontSize: 10, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: "#3a3a3a" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading && <SkeletonRows />}
                {!loading && fixes.length === 0 && !error && (
                  <tr><td colSpan={6} style={{ padding: "60px 16px", textAlign: "center", color: "#3a3a3a", fontFamily: tokens.font, fontSize: 13 }}>No fixes found.</td></tr>
                )}
                {!loading && fixes.map(fix => (
                  <tr
                    key={fix.id}
                    style={{ borderBottom: "1px solid rgba(255,255,255,0.04)", transition: "background 0.12s" }}
                    onMouseEnter={e => (e.currentTarget.style.background = "rgba(255,255,255,0.02)")}
                    onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                  >
                    <td style={{ padding: "13px 16px", color: "#555", fontSize: 11, fontFamily: "'DM Mono', monospace" }}>
                      {fix.id.slice(0, 12)}…
                    </td>
                    <td style={{ padding: "13px 16px" }}>
                      {fix.issue_id ? (
                        <Link href={`/issues/${fix.issue_id}`} style={{ color: tokens.textDim, textDecoration: "none" }}>
                          {fix.issue_title ?? fix.issue_id.slice(0, 10) + "…"}
                        </Link>
                      ) : "—"}
                    </td>
                    <td style={{ padding: "13px 16px" }}><StatusBadge status={fix.status} /></td>
                    <td style={{ padding: "13px 16px", color: "#555", fontSize: 12 }}>
                      {fix.files_count != null ? `${fix.files_count} file${fix.files_count !== 1 ? "s" : ""}` : "—"}
                    </td>
                    <td style={{ padding: "13px 16px", color: "#555", fontSize: 12 }}>
                      {new Date(fix.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                    </td>
                    <td style={{ padding: "13px 16px", textAlign: "right" }}>
                      <Link href={`/fixes/${fix.id}`} style={{
                        display: "inline-flex", alignItems: "center", gap: 4,
                        fontSize: 12, color: "#555", textDecoration: "none", transition: "color 0.15s",
                      }}
                        onMouseEnter={e => (e.currentTarget.style.color = "#a855f7")}
                        onMouseLeave={e => (e.currentTarget.style.color = "#555")}
                      >
                        Review <ChevronRight />
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
