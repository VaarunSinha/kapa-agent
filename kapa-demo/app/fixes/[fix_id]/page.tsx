"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Shell, PageHeader, StatusBadge, ErrorBanner, tokens } from "@/components/shared";
import { FixPreview } from "@/components/FixPreview";
import { FixChatPanel } from "@/components/FixChatPanel";

interface Fix {
  id: string;
  issue_id: string;
  status: string;
  files: { file_path: string; diff?: string; markdown?: string }[];
  created_at: string;
}

export default function FixReviewPage() {
  const { fix_id } = useParams<{ fix_id: string }>();

  const [fix, setFix] = useState<Fix | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!fix_id) return;
    fetch(`/api/fixes/${fix_id}`)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setFix)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
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
          {/* Left: diff/preview */}
          <FixPreview fix={fix} loading={loading} />

          {/* Right: chat */}
          <FixChatPanel />
        </div>
      </div>
    </Shell>
  );
}
