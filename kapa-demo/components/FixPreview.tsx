"use client";
import { useState } from "react";
import { Card, SectionLabel, Skeleton, FileIcon, tokens } from "./shared";

interface FileFix {
  file_path: string;
  diff?: string;
  markdown?: string;
}

interface Fix {
  id: string;
  issue_id: string;
  status: string;
  files: FileFix[];
  created_at: string;
}

function DiffLine({ line }: { line: string }) {
  const isAdd = line.startsWith("+") && !line.startsWith("+++");
  const isDel = line.startsWith("-") && !line.startsWith("---");
  const isMeta = line.startsWith("@@") || line.startsWith("---") || line.startsWith("+++");
  return (
    <div style={{
      padding: "1px 12px",
      background: isAdd ? "rgba(34,197,94,0.08)" : isDel ? "rgba(239,68,68,0.08)" : isMeta ? "rgba(168,85,247,0.06)" : "transparent",
      borderLeft: isAdd ? "2px solid rgba(34,197,94,0.4)" : isDel ? "2px solid rgba(239,68,68,0.4)" : isMeta ? "2px solid rgba(168,85,247,0.3)" : "2px solid transparent",
      color: isAdd ? "#86efac" : isDel ? "#fca5a5" : isMeta ? "#c084fc" : "#888",
      fontSize: 12,
      fontFamily: "'DM Mono', monospace",
      lineHeight: 1.7,
      whiteSpace: "pre",
    }}>{line}</div>
  );
}

function MarkdownPreview({ content }: { content: string }) {
  return (
    <div style={{
      padding: "16px 20px", fontSize: 13, lineHeight: 1.8,
      color: tokens.textDim, fontFamily: "'DM Mono', monospace",
      whiteSpace: "pre-wrap", wordBreak: "break-word",
    }}>{content}</div>
  );
}

function FileTab({ file, active, onClick }: { file: FileFix; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} style={{
      display: "flex", alignItems: "center", gap: 6,
      padding: "6px 12px", borderRadius: 6, border: "none", cursor: "pointer",
      background: active ? "rgba(168,85,247,0.15)" : "transparent",
      color: active ? "#c084fc" : "#555",
      fontSize: 12, fontFamily: tokens.font,
      transition: "all 0.15s", whiteSpace: "nowrap",
    }}>
      <FileIcon />
      <span>{file.file_path.split("/").pop()}</span>
    </button>
  );
}

export function FixPreview({ fix, loading }: { fix: Fix | null; loading?: boolean }) {
  const [activeIdx, setActiveIdx] = useState(0);
  const [mode, setMode] = useState<"diff" | "preview">("diff");

  if (loading) {
    return (
      <Card style={{ padding: 24, height: "100%", display: "flex", flexDirection: "column", gap: 14 }}>
        <SectionLabel icon={<FileIcon />} label="Proposed Changes" />
        <Skeleton h={12} w="50%" /><Skeleton h={200} />
      </Card>
    );
  }

  if (!fix || !fix.files?.length) {
    return (
      <Card style={{ padding: 24, display: "flex", alignItems: "center", justifyContent: "center", minHeight: 300 }}>
        <p style={{ fontSize: 13, color: "#444", fontFamily: tokens.font }}>No fix available yet.</p>
      </Card>
    );
  }

  const activeFile = fix.files[activeIdx];

  return (
    <Card style={{ display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
      {/* Header */}
      <div style={{
        padding: "14px 18px",
        borderBottom: `1px solid ${tokens.border}`,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        flexShrink: 0,
      }}>
        <SectionLabel icon={<FileIcon />} label="Proposed Changes" />
        <div style={{ display: "flex", gap: 4 }}>
          {(["diff", "preview"] as const).map(m => (
            <button key={m} onClick={() => setMode(m)} style={{
              padding: "4px 10px", borderRadius: 5, border: "none", cursor: "pointer",
              background: mode === m ? "rgba(168,85,247,0.15)" : "transparent",
              color: mode === m ? "#a855f7" : "#555",
              fontSize: 11, fontWeight: 600, fontFamily: tokens.font,
              textTransform: "uppercase", letterSpacing: "0.06em",
            }}>{m}</button>
          ))}
        </div>
      </div>

      {/* File tabs */}
      {fix.files.length > 1 && (
        <div style={{
          display: "flex", gap: 4, padding: "8px 14px",
          borderBottom: `1px solid ${tokens.border}`,
          overflowX: "auto", flexShrink: 0,
        }}>
          {fix.files.map((f, i) => (
            <FileTab key={i} file={f} active={activeIdx === i} onClick={() => setActiveIdx(i)} />
          ))}
        </div>
      )}

      {/* File path breadcrumb */}
      <div style={{
        padding: "6px 18px",
        borderBottom: `1px solid ${tokens.border}`,
        display: "flex", alignItems: "center", gap: 6,
        flexShrink: 0,
      }}>
        <FileIcon />
        <span style={{ fontSize: 11, color: "#555", fontFamily: tokens.font }}>{activeFile.file_path}</span>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: "auto" }}>
        {mode === "diff" && activeFile.diff ? (
          <div style={{ padding: "8px 0" }}>
            {activeFile.diff.split("\n").map((line, i) => (
              <DiffLine key={i} line={line} />
            ))}
          </div>
        ) : activeFile.markdown ? (
          <MarkdownPreview content={activeFile.markdown} />
        ) : (
          <div style={{ padding: 24, color: "#444", fontSize: 13, fontFamily: tokens.font }}>
            No content available for this view mode.
          </div>
        )}
      </div>
    </Card>
  );
}
