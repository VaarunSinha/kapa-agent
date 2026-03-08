"use client";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Card, SectionLabel, FileIcon, SpinIcon, tokens } from "./shared";

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

function DiffLine({ line, updatedByFixAssistant }: { line: string; updatedByFixAssistant?: boolean }) {
  const isAdd = line.startsWith("+") && !line.startsWith("+++");
  const isDel = line.startsWith("-") && !line.startsWith("---");
  const isMeta = line.startsWith("@@") || line.startsWith("---") || line.startsWith("+++");
  const useFixAssistantColour = updatedByFixAssistant && isAdd;
  return (
    <div style={{
      padding: "1px 12px",
      background: useFixAssistantColour ? "rgba(6,182,212,0.12)" : isAdd ? "rgba(34,197,94,0.08)" : isDel ? "rgba(239,68,68,0.08)" : isMeta ? "rgba(168,85,247,0.06)" : "transparent",
      borderLeft: useFixAssistantColour ? "2px solid rgba(6,182,212,0.5)" : isAdd ? "2px solid rgba(34,197,94,0.4)" : isDel ? "2px solid rgba(239,68,68,0.4)" : isMeta ? "2px solid rgba(168,85,247,0.3)" : "2px solid transparent",
      color: useFixAssistantColour ? "#67e8f9" : isAdd ? "#86efac" : isDel ? "#fca5a5" : isMeta ? "#c084fc" : "#888",
      fontSize: 12,
      fontFamily: "'DM Mono', monospace",
      lineHeight: 1.7,
      whiteSpace: "pre",
    }}>{line}</div>
  );
}

function MarkdownPreview({ content }: { content: string }) {
  return (
    <div
      className="fix-preview-markdown"
      style={{
        padding: "16px 20px",
        fontSize: 13,
        lineHeight: 1.8,
        color: tokens.textDim,
        fontFamily: tokens.font,
        wordBreak: "break-word",
      }}
    >
      <ReactMarkdown
        components={{
          h1: ({ children }) => <h1 style={{ fontSize: 18, fontWeight: 700, margin: "16px 0 8px", color: "#e2e8f0" }}>{children}</h1>,
          h2: ({ children }) => <h2 style={{ fontSize: 16, fontWeight: 600, margin: "14px 0 6px", color: "#cbd5e1" }}>{children}</h2>,
          h3: ({ children }) => <h3 style={{ fontSize: 14, fontWeight: 600, margin: "12px 0 4px", color: "#94a3b8" }}>{children}</h3>,
          p: ({ children }) => <p style={{ margin: "0 0 8px" }}>{children}</p>,
          ul: ({ children }) => <ul style={{ margin: "4px 0 12px", paddingLeft: 20 }}>{children}</ul>,
          ol: ({ children }) => <ol style={{ margin: "4px 0 12px", paddingLeft: 20 }}>{children}</ol>,
          li: ({ children }) => <li style={{ marginBottom: 2 }}>{children}</li>,
          code: ({ className, children }) => {
            const isBlock = className?.startsWith("language-");
            if (isBlock) {
              return (
                <pre style={{
                  background: "rgba(0,0,0,0.25)",
                  padding: 12,
                  borderRadius: 6,
                  overflow: "auto",
                  margin: "8px 0",
                  fontSize: 12,
                  fontFamily: "'DM Mono', monospace",
                }}>
                  <code>{children}</code>
                </pre>
              );
            }
            return (
              <code style={{
                background: "rgba(0,0,0,0.2)",
                padding: "2px 6px",
                borderRadius: 4,
                fontSize: 12,
                fontFamily: "'DM Mono', monospace",
              }}>{children}</code>
            );
          },
          pre: ({ children }) => <>{children}</>,
          blockquote: ({ children }) => (
            <blockquote style={{ borderLeft: "3px solid #64748b", margin: "8px 0", paddingLeft: 12, color: "#94a3b8" }}>
              {children}
            </blockquote>
          ),
          strong: ({ children }) => <strong style={{ fontWeight: 600 }}>{children}</strong>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: "#67e8f9", textDecoration: "underline" }}>
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
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

export function FixPreview({ fix, loading, generating, applying, updatedByFixAssistant, onClearFixAssistantIndicator }: { fix: Fix | null; loading?: boolean; generating?: boolean; applying?: boolean; updatedByFixAssistant?: boolean; onClearFixAssistantIndicator?: () => void }) {
  const [activeIdx, setActiveIdx] = useState(0);
  const [mode, setMode] = useState<"diff" | "preview">("diff");

  useEffect(() => {
    if (!updatedByFixAssistant || !onClearFixAssistantIndicator) return;
    const t = setTimeout(onClearFixAssistantIndicator, 6000);
    return () => clearTimeout(t);
  }, [updatedByFixAssistant, onClearFixAssistantIndicator]);

  const handleInteraction = () => {
    if (updatedByFixAssistant) onClearFixAssistantIndicator?.();
  };

  const showGenerating = loading || generating || (fix && !fix.files?.length);
  if (showGenerating) {
    return (
      <Card style={{ padding: 24, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 300, gap: 12 }}>
        <SpinIcon />
        <p style={{ fontSize: 13, color: "#555", fontFamily: tokens.font }}>Generating fix…</p>
      </Card>
    );
  }

  if (!fix || !fix.files?.length) {
    return (
      <Card style={{ padding: 24, display: "flex", alignItems: "center", justifyContent: "center", minHeight: 300 }}>
        <p style={{ fontSize: 13, color: "#444", fontFamily: tokens.font }}>No fix available.</p>
      </Card>
    );
  }

  const activeFile = fix.files[activeIdx];

  if (applying) {
    return (
      <Card style={{ padding: 24, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 300, gap: 12 }}>
        <SpinIcon />
        <p style={{ fontSize: 13, color: "#555", fontFamily: tokens.font }}>Applying your changes…</p>
      </Card>
    );
  }

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
            <button key={m} onClick={() => { setMode(m); handleInteraction(); }} style={{
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
            <FileTab key={i} file={f} active={activeIdx === i} onClick={() => { setActiveIdx(i); handleInteraction(); }} />
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
      <div style={{ flex: 1, overflow: "auto" }} onClick={handleInteraction}>
        {mode === "diff" && activeFile.diff ? (
          <div style={{
            padding: "8px 0",
            ...(updatedByFixAssistant ? { background: "rgba(6,182,212,0.04)", borderLeft: "3px solid rgba(6,182,212,0.35)", marginLeft: 0 } : {}),
          }}>
            {updatedByFixAssistant && (
              <div style={{
                padding: "6px 12px",
                fontSize: 11,
                color: "#67e8f9",
                fontFamily: tokens.font,
                borderBottom: "1px solid rgba(6,182,212,0.2)",
                marginBottom: 4,
              }}>
                This colour means updated by Fix Assistant.
              </div>
            )}
            {activeFile.diff.split("\n").map((line, i) => (
              <DiffLine key={i} line={line} updatedByFixAssistant={updatedByFixAssistant} />
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
