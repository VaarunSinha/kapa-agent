"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Shell, PageHeader, Card, SectionLabel, StatusBadge, Skeleton, ErrorBanner, Button, tokens, SparkleIcon, ChevronRight } from "@/components/shared";
import { IssueHeader } from "@/components/IssueHeader";
import { ResearchPanel } from "@/components/ResearchPanel";
import { QuestionsForm } from "@/components/QuestionsForm";

interface Issue {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

interface Research {
  id: string;
  summary: string;
  files_analyzed: string[];
  confidence_score: number;
  status: string;
}

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

export default function IssueDetailPage() {
  const { id } = useParams<{ id: string }>();

  const [issue, setIssue] = useState<Issue | null>(null);
  const [research, setResearch] = useState<Research | null>(null);
  const [questionsData, setQuestionsData] = useState<QuestionsData | null>(null);

  const [issueLoading, setIssueLoading] = useState(true);
  const [researchLoading, setResearchLoading] = useState(true);
  const [questionsLoading, setQuestionsLoading] = useState(true);

  const [issueError, setIssueError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    // Fetch issue
    fetch(`/api/issues/${id}`)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setIssue)
      .catch(e => setIssueError(e.message))
      .finally(() => setIssueLoading(false));

    // Fetch research
    fetch(`/api/research/${id}`)
      .then(r => { if (!r.ok) return null; return r.json(); })
      .then(data => { if (data) setResearch(data); })
      .catch(() => {})
      .finally(() => setResearchLoading(false));
  }, [id]);

  // Fetch questions once we have research id
  useEffect(() => {
    if (!research?.id) { setQuestionsLoading(false); return; }
    fetch(`/api/questions/${research.id}`)
      .then(r => { if (!r.ok) return null; return r.json(); })
      .then(data => { if (data) setQuestionsData(data); })
      .catch(() => {})
      .finally(() => setQuestionsLoading(false));
  }, [research?.id]);

  return (
    <Shell>
      <PageHeader
        title={issueLoading ? "Loading…" : issue?.title ?? "Issue"}
        back={{ href: "/issues", label: "All Issues" }}
      >
        {issue && (
          <Link href={`/fixes/${issue.id}`} style={{ textDecoration: "none" }}>
            <Button variant="primary">
              <SparkleIcon /> View Fix <ChevronRight />
            </Button>
          </Link>
        )}
      </PageHeader>

      <div style={{ padding: "28px 40px", display: "flex", flexDirection: "column", gap: 24 }}>
        {issueError && <ErrorBanner message={issueError} />}

        {/* Issue header */}
        {issueLoading ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <Skeleton h={12} w="20%" /><Skeleton h={28} w="60%" /><Skeleton h={12} w="80%" />
          </div>
        ) : issue ? (
          <IssueHeader issue={issue} />
        ) : null}

        {/* Research */}
        <ResearchPanel research={research} loading={researchLoading} />

        {/* Questions */}
        <Card style={{ padding: 24 }}>
          <SectionLabel icon={<SparkleIcon />} label="Questions" />
          {questionsLoading ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <Skeleton h={14} w="70%" /><Skeleton h={40} /><Skeleton h={14} w="60%" /><Skeleton h={40} />
            </div>
          ) : questionsData && questionsData.questions.length > 0 ? (
            <QuestionsForm
              researchId={questionsData.research_id}
              questions={questionsData.questions}
            />
          ) : (
            <p style={{ fontSize: 13, color: "#444", fontFamily: tokens.font }}>
              No questions available yet.
            </p>
          )}
        </Card>
      </div>
    </Shell>
  );
}
