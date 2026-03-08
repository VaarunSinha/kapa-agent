"use client";
import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Shell, PageHeader, StatusBadge, ErrorBanner } from "@/components/shared";
import { FixPreview } from "@/components/FixPreview";
import { FixChatPanel } from "@/components/FixChatPanel";

const API_BASE = typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL
  ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
  : "";

const POLL_INTERVAL_MS = 3000;
const POLL_TIMEOUT_MS = 120000;

interface Fix {
  id: string;
  issue_id: string;
  status: string;
  files: { file_path: string; diff?: string; markdown?: string }[];
  created_at: string;
  assistant_intro?: string;
  assistant_reply_success?: string;
}

export default function FixReviewPage() {
  const { fix_id } = useParams<{ fix_id: string }>();
  const router = useRouter();
  const [fix, setFix] = useState<Fix | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [applying, setApplying] = useState(false);
  const [updatedByFixAssistant, setUpdatedByFixAssistant] = useState(false);
  const pollUntil = useRef<number>(0);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!fix_id) return;

    function stopPolling() {
      if (pollTimer.current) {
        clearInterval(pollTimer.current);
        pollTimer.current = null;
      }
      setGenerating(false);
    }

    function poll() {
      if (Date.now() >= pollUntil.current) {
        stopPolling();
        setError("Fix is taking longer than expected. Please try again from the issue page.");
        return;
      }
      fetch(`${API_BASE}/api/fixes/${fix_id}`)
        .then(r => {
          if (r.status === 404) return null;
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then(data => {
          if (data?.files?.length) {
            setFix(data);
            stopPolling();
            setError(null);
          }
        })
        .catch(e => {
          stopPolling();
          setError(e.message);
        });
    }

    fetch(`${API_BASE}/api/fixes/${fix_id}`)
      .then(r => {
        if (r.status === 404) {
          setGenerating(true);
          pollUntil.current = Date.now() + POLL_TIMEOUT_MS;
          poll();
          pollTimer.current = setInterval(poll, POLL_INTERVAL_MS);
          return null;
        }
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(data => {
        if (data) {
          setFix(data);
          setError(null);
        }
      })
      .catch(e => {
        setError(e.message);
      })
      .finally(() => setLoading(false));

    return () => {
      if (pollTimer.current) clearInterval(pollTimer.current);
    };
  }, [fix_id]);

  return (
    <Shell>
      <PageHeader
        title="Fix Review"
        subtitle="Review the proposed documentation changes and request edits via the AI assistant."
        back={{ href: fix?.issue_id ? `/issues/${fix.issue_id}` : "/issues", label: "Back to Issue" }}
      >
        {fix && <StatusBadge status={fix.status} />}
      </PageHeader>

      <div style={{ padding: "24px 32px", display: "flex", flexDirection: "column", gap: 16 }}>
        {error && <ErrorBanner message={error} />}

        {/* Split panel */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 380px",
          gap: 16,
          height: "calc(100vh - 160px)",
          minHeight: 500,
        }}>
          {/* Left: diff/preview; show "Applying your changes…" when chat is applying */}
          <FixPreview
            fix={fix}
            loading={loading}
            generating={generating && !fix}
            applying={applying}
            updatedByFixAssistant={updatedByFixAssistant}
            onClearFixAssistantIndicator={() => setUpdatedByFixAssistant(false)}
          />

          {/* Right: chat + approve */}
          <FixChatPanel
            fixId={fix?.id ?? fix_id ?? ""}
            fix={fix}
            onFixUpdated={(updated) => {
              if (updated.files) {
                setFix(prev => (prev ? { ...prev, files: updated.files } : prev));
                setUpdatedByFixAssistant(true);
              }
            }}
            onApprove={() => router.push(fix?.issue_id ? `/issues/${fix.issue_id}` : "/fixes")}
            apiBase={API_BASE}
            onThinkingChange={setApplying}
          />
        </div>
      </div>
    </Shell>
  );
}
