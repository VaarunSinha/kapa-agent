"use client";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";

const API_BASE = typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL
  ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
  : "http://localhost:8000";

/**
 * GitHub redirects here after app installation (e.g. /setup?installation_id=...&setup_action=install).
 * We forward to the backend /github/setup so it can clone, generate understanding, then redirect back to /github/setup?done=1.
 */
function SetupRedirectContent() {
  const searchParams = useSearchParams();
  const [redirected, setRedirected] = useState(false);

  useEffect(() => {
    const installationId = searchParams.get("installation_id");
    const setupAction = searchParams.get("setup_action");
    const params = new URLSearchParams();
    if (installationId) params.set("installation_id", installationId);
    if (setupAction) params.set("setup_action", setupAction);
    const qs = params.toString();
    const backendUrl = `${API_BASE}/github/setup${qs ? `?${qs}` : ""}`;
    setRedirected(true);
    window.location.href = backendUrl;
  }, [searchParams]);

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "#0a0a0c",
      color: "#9a9a9a",
      fontFamily: "'DM Mono', monospace",
      fontSize: 14,
    }}>
      {redirected ? "Redirecting to complete setup…" : "Loading…"}
    </div>
  );
}

export default function SetupPage() {
  return (
    <Suspense fallback={
      <div style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#0a0a0c",
        color: "#9a9a9a",
        fontFamily: "'DM Mono', monospace",
      }}>
        Loading…
      </div>
    }>
      <SetupRedirectContent />
    </Suspense>
  );
}
