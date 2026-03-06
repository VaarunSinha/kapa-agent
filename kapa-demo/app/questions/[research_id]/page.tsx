"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Shell, PageHeader, Card, Skeleton, ErrorBanner, tokens } from "@/components/shared";
import { QuestionsForm } from "@/components/QuestionsForm";

interface Question {
  id: string;
  type: "text" | "textarea" | "radiogroup" | "checkbox";
  title: string;
  choices?: string[];
  required?: boolean;
}

interface QuestionsData {
  research_id: string;
  questions: Question[];
}

export default function QuestionsPage() {
  const { research_id } = useParams<{ research_id: string }>();
  const router = useRouter();

  const [data, setData] = useState<QuestionsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!research_id) return;
    fetch(`/api/questions/${research_id}`)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [research_id]);

  return (
    <Shell>
      <PageHeader
        title="Survey Questions"
        subtitle="Answer these questions to help refine the documentation fix."
        back={{ href: "/research", label: "Research" }}
      />
      <div style={{ padding: "32px 40px", maxWidth: 760 }}>
        {error && <ErrorBanner message={error} />}

        {loading && (
          <Card style={{ padding: 28, display: "flex", flexDirection: "column", gap: 14 }}>
            <Skeleton h={12} w="40%" />
            <Skeleton h={44} />
            <Skeleton h={12} w="55%" />
            <Skeleton h={44} />
            <Skeleton h={12} w="35%" />
            <Skeleton h={88} />
          </Card>
        )}

        {!loading && !error && data && (
          <>
            {data.questions.length === 0 ? (
              <Card style={{ padding: 32, textAlign: "center" }}>
                <p style={{ fontSize: 13, color: "#444", fontFamily: tokens.font }}>No questions found for this research task.</p>
              </Card>
            ) : (
              <Card style={{ padding: 24 }}>
                <QuestionsForm
                  researchId={data.research_id}
                  questions={data.questions}
                  onSubmitSuccess={() => {
                    setTimeout(() => router.push("/research"), 1800);
                  }}
                />
              </Card>
            )}
          </>
        )}
      </div>
    </Shell>
  );
}
