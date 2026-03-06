"use client";
import { StatusBadge, tokens } from "./shared";

interface Issue {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

export function IssueHeader({ issue }: { issue: Issue }) {
  const date = new Date(issue.created_at).toLocaleDateString("en-US", {
    year: "numeric", month: "short", day: "numeric",
  });

  return (
    <div style={{ marginBottom: 28 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <StatusBadge status={issue.status} />
        <span style={{ fontSize: 12, color: "#444", fontFamily: tokens.font }}>#{issue.id.slice(0, 8)}</span>
        <span style={{ fontSize: 12, color: "#444", fontFamily: tokens.font }}>Created {date}</span>
      </div>
      <h2 style={{ fontSize: 22, fontWeight: 700, color: tokens.text, letterSpacing: "-0.015em", marginBottom: 10 }}>
        {issue.title}
      </h2>
      <p style={{ fontSize: 13, color: tokens.textDim, lineHeight: 1.7, maxWidth: 700 }}>
        {issue.description}
      </p>
    </div>
  );
}
