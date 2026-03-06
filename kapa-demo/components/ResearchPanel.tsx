"use client";
import { Card, SectionLabel, Skeleton, FileIcon, BrainIcon, tokens } from "./shared";

interface Research {
  id: string;
  summary: string;
  files_analyzed: string[];
  confidence_score: number;
  status: string;
}

function ConfidenceBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = pct >= 75 ? "#4ade80" : pct >= 45 ? "#fbbf24" : "#f87171";
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontSize: 12, color: "#555", fontFamily: tokens.font }}>Confidence</span>
        <span style={{ fontSize: 12, fontWeight: 700, color, fontFamily: tokens.font }}>{pct}%</span>
      </div>
      <div style={{ height: 4, background: "rgba(255,255,255,0.06)", borderRadius: 2, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${pct}%`, background: color, borderRadius: 2, transition: "width 0.6s ease" }} />
      </div>
    </div>
  );
}

export function ResearchPanel({ research, loading }: { research: Research | null; loading?: boolean }) {
  if (loading) {
    return (
      <Card style={{ padding: 24 }}>
        <SectionLabel icon={<BrainIcon />} label="Research" />
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <Skeleton h={12} w="90%" /><Skeleton h={12} w="75%" /><Skeleton h={12} w="55%" />
        </div>
      </Card>
    );
  }

  if (!research) {
    return (
      <Card style={{ padding: 24 }}>
        <SectionLabel icon={<BrainIcon />} label="Research" />
        <p style={{ fontSize: 13, color: "#444", fontFamily: tokens.font }}>Research not yet available for this issue.</p>
      </Card>
    );
  }

  return (
    <Card style={{ padding: 24 }}>
      <SectionLabel icon={<BrainIcon />} label="Research" />

      {/* Summary */}
      <div style={{ marginBottom: 20 }}>
        <p style={{ fontSize: 13, color: tokens.textDim, lineHeight: 1.75, fontFamily: tokens.font }}>
          {research.summary}
        </p>
      </div>

      {/* Confidence */}
      <div style={{ marginBottom: 20 }}>
        <ConfidenceBar score={research.confidence_score ?? 0} />
      </div>

      {/* Files analyzed */}
      {research.files_analyzed && research.files_analyzed.length > 0 && (
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#444", marginBottom: 10, fontFamily: tokens.font }}>
            Files Analyzed ({research.files_analyzed.length})
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {research.files_analyzed.map((f, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "6px 10px", borderRadius: 6,
                background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)",
              }}>
                <span style={{ color: "#a855f7" }}><FileIcon /></span>
                <span style={{ fontSize: 12, color: "#888", fontFamily: "'DM Mono', monospace" }}>{f}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
