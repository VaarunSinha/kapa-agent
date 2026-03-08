"use client";
import { useState, useEffect } from "react";
import { Model } from "survey-core";
import { Survey } from "survey-react-ui";
import "survey-core/survey-core.min.css";
import { tokens } from "./shared";

interface Question {
  id: string;
  type: "text" | "textarea" | "radiogroup" | "checkbox" | "comment" | "multiple_choice";
  title: string;
  choices?: string[];
  required?: boolean;
}

interface QuestionsFormProps {
  researchId: string;
  questions: Question[];
  onSubmitSuccess?: (answers: Record<string, any>) => void;
}

// Map our API question types to SurveyJS element types
function toSurveyElements(questions: Question[]) {
  return questions.map((q) => {
    const type =
      q.type === "textarea" ? "comment" :
      q.type === "multiple_choice" ? "radiogroup" :
      q.type;
    const choices = Array.isArray(q.choices) ? q.choices : [];
    return {
      name: q.id,
      type,
      title: q.title,
      isRequired: q.required ?? false,
      ...(type === "radiogroup" ? { choices } : {}),
    };
  });
}

export function QuestionsForm({ researchId, questions, onSubmitSuccess }: QuestionsFormProps) {
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const survey = new Model({
    elements: toSurveyElements(questions),
    showCompletedPage: false,
    completeText: "Submit Answers",
  });

  // Apply dark theme overrides via CSS vars on mount
  useEffect(() => {
    const style = document.createElement("style");
    style.id = "survey-dark-override";
    style.textContent = `
      .sd-root-modern {
        --background: #111113;
        --background-dim: #0e0e10;
        --background-dim-light: #18181b;
        --primary: #a855f7;
        --primary-light: rgba(168,85,247,0.15);
        --foreground: #f0f0f0;
        --base-unit: 8px;
        font-family: 'DM Mono', 'Fira Code', monospace !important;
      }
      .sd-root-modern .sd-body { background: transparent; }
      .sd-root-modern .sd-page { padding: 0; }
      .sd-root-modern input,
      .sd-root-modern textarea,
      .sd-root-modern .sd-input {
        color: var(--foreground) !important;
      }
    `;
    if (!document.getElementById("survey-dark-override")) {
      document.head.appendChild(style);
    }
    return () => { style.remove(); };
  }, []);

  survey.onComplete.add(async (sender) => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch("/api/questions/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ research_id: researchId, answers: sender.data }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setSubmitted(true);
      onSubmitSuccess?.(sender.data);
    } catch (e: any) {
      setError(e.message);
      // Allow re-submission
      sender.clear(false, true);
    } finally {
      setSubmitting(false);
    }
  });

  if (submitted) {
    return (
      <div style={{
        padding: "32px 24px", textAlign: "center",
        background: "rgba(34,197,94,0.06)",
        border: "1px solid rgba(34,197,94,0.2)",
        borderRadius: 10,
        fontFamily: tokens.font,
      }}>
        <div style={{ fontSize: 28, marginBottom: 10 }}>✓</div>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#4ade80", marginBottom: 6 }}>Answers submitted</div>
        <div style={{ fontSize: 12, color: "#555" }}>Your responses have been recorded.</div>
      </div>
    );
  }

  return (
    <div>
      {error && (
        <div style={{
          marginBottom: 12, padding: "10px 14px", borderRadius: 8,
          background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
          color: "#f87171", fontSize: 12, fontFamily: tokens.font,
        }}>
          ⚠ {error} — please try again.
        </div>
      )}
      <div style={{ opacity: submitting ? 0.6 : 1, transition: "opacity 0.2s", pointerEvents: submitting ? "none" : "auto" }}>
        <Survey model={survey} />
      </div>
    </div>
  );
}
