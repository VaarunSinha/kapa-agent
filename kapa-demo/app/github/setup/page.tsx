"use client";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Shell, PageHeader, Card, Button, ErrorBanner, tokens } from "@/components/shared";

const API_BASE = typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL
  ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
  : "";

interface Installation {
  installation_id: number;
  owner: string;
  repository_name: string;
  installed_at: string | null;
  understanding: string;
  source_status?: string;
}

const POLL_INTERVAL_MS = 2500;

function GitHubSetupContent() {
  const searchParams = useSearchParams();
  const installationId = searchParams.get("installation_id");
  const done = searchParams.get("done");

  const [installation, setInstallation] = useState<Installation | null>(null);
  const [understanding, setUnderstanding] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const url = installationId
    ? `${API_BASE}/api/github/installation?installation_id=${installationId}`
    : `${API_BASE}/api/github/installation`;

  useEffect(() => {
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        setInstallation(data);
        setUnderstanding(data.understanding || "");
        setError(null);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [installationId]);

  // When done=1 and source_status is not ready, poll until real understanding has loaded
  const stillIndexing = Boolean(
    done === "1" &&
    installation &&
    installation.source_status !== "ready" &&
    installation.source_status !== "failed"
  );

  useEffect(() => {
    if (!stillIndexing || !installationId) return;
    const interval = setInterval(() => {
      fetch(url)
        .then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then((data) => {
          setInstallation(data);
          setUnderstanding(data.understanding || "");
        })
        .catch(() => {});
    }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [stillIndexing, installationId, url]);

  const handleSave = () => {
    if (!installation) return;
    setSaving(true);
    setError(null);
    fetch(`${API_BASE}/api/github/installation`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        installation_id: installation.installation_id,
        understanding,
      }),
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
      })
      .catch((e) => setError(e.message))
      .finally(() => setSaving(false));
  };

  if (loading) {
    return (
      <Shell>
        <PageHeader title="GitHub Setup" subtitle="Setting up your repository connection…" />
        <div style={{ padding: "32px 40px" }}>
          <Card style={{ padding: 48, textAlign: "center" }}>
            <p style={{ fontSize: 14, color: tokens.textDim, fontFamily: tokens.font }}>Loading…</p>
          </Card>
        </div>
      </Shell>
    );
  }

  if (error && !installation) {
    return (
      <Shell>
        <PageHeader title="GitHub Setup" subtitle="Something went wrong." />
        <div style={{ padding: "32px 40px" }}>
          <ErrorBanner message={error} />
          <p style={{ marginTop: 16, fontSize: 13, color: tokens.textDim, fontFamily: tokens.font }}>
            You may have been redirected here before the installation was recorded. Try{" "}
            <Link href="/dashboard" style={{ color: tokens.purple }}>Connect Source Code</Link> from Coverage Gaps again.
          </p>
        </div>
      </Shell>
    );
  }

  if (stillIndexing) {
    return (
      <Shell>
        <PageHeader title="GitHub Setup" subtitle="Setting up your repository connection…" />
        <div style={{ padding: "32px 40px" }}>
          <Card style={{ padding: 48, textAlign: "center" }}>
            <p style={{ fontSize: 14, color: tokens.textDim, fontFamily: tokens.font, marginBottom: 8 }}>
              Loading repository understanding…
            </p>
            <p style={{ fontSize: 12, color: "#555", fontFamily: tokens.font }}>
              Cloning repo, indexing docs, and generating understanding. This may take a minute.
            </p>
          </Card>
        </div>
      </Shell>
    );
  }

  return (
    <Shell>
      <PageHeader
        title="GitHub Setup"
        subtitle={done === "1" ? "Repository understanding generated. Review or edit below." : "Review and edit repository understanding."}
        back={{ href: "/dashboard", label: "Coverage Gaps" }}
      />
      <div style={{ padding: "32px 40px", maxWidth: 900 }}>
        {error && <ErrorBanner message={error} />}
        {installation && (
          <Card style={{ padding: 24 }}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.08em", color: "#555", marginBottom: 6, fontFamily: tokens.font }}>REPOSITORY</div>
              <div style={{ fontSize: 14, color: tokens.text, fontFamily: tokens.font }}>{installation.owner}/{installation.repository_name}</div>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label htmlFor="github-understanding" style={{ display: "block", fontSize: 11, fontWeight: 600, letterSpacing: "0.08em", color: "#555", marginBottom: 6, fontFamily: tokens.font }}>UNDERSTANDING (markdown)</label>
              <textarea
                id="github-understanding"
                value={understanding}
                onChange={(e) => setUnderstanding(e.target.value)}
                rows={16}
                style={{
                  width: "100%",
                  padding: 12,
                  borderRadius: 8,
                  border: `1px solid ${tokens.border}`,
                  background: "rgba(255,255,255,0.03)",
                  color: tokens.text,
                  fontSize: 13,
                  fontFamily: "'DM Mono', monospace",
                  lineHeight: 1.6,
                  resize: "vertical",
                }}
              />
            </div>
            <Button onClick={handleSave} loading={saving} disabled={saving}>Save changes</Button>
          </Card>
        )}
      </div>
    </Shell>
  );
}

export default function GitHubSetupPage() {
  return (
    <Suspense fallback={
      <Shell>
        <PageHeader title="GitHub Setup" subtitle="Loading…" />
        <div style={{ padding: 32 }} />
      </Shell>
    }>
      <GitHubSetupContent />
    </Suspense>
  );
}
