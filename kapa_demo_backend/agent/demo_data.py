"""
Helpers to create sample research, questions, and fix for an issue (for demo/testing).
Used by load_sample_data management command and by CoverageGapActAPIView after Act.
"""
from .models import Issue, Research, Question, Fix


def create_sample_fix_for_issue(issue, file_path="docs/getting-started.md", summary="Add installation steps"):
    return Fix.objects.create(
        issue=issue,
        file_path=file_path,
        patch="""--- a/docs/getting-started.md
+++ b/docs/getting-started.md
@@ -1,3 +1,15 @@
 # Getting Started
+
+## Installation
+
+1. Install the CLI:
+   ```bash
+   npm install -g @kapa/cli
+   ```
+2. Log in:
+   ```bash
+   kapa login
+   ```
""",
        summary=summary,
        status="draft",
    )


def create_sample_questions_for_research(research):
    Question.objects.create(
        research=research,
        question_text="How often do users run into this gap in practice?",
        question_type="choice",
        choices=["Rarely", "Sometimes", "Often", "Very often"],
    )
    Question.objects.create(
        research=research,
        question_text="Should we add a code example here?",
        question_type="choice",
        choices=["Yes", "No", "Only if simple"],
    )
    Question.objects.create(
        research=research,
        question_text="Any other context we should include?",
        question_type="textarea",
    )


def create_sample_research_for_issue(issue, summary=None, confidence=0.82):
    if summary is None:
        summary = (
            "Analyzed 3 doc files and 12 conversation snippets. "
            "The gap appears when users ask about installation; the current docs jump to usage. "
            "Recommend adding a short 'Installation' section with CLI and npm options."
        )
    research = Research.objects.create(
        issue=issue,
        summary=summary,
        files_analyzed=[
            "docs/README.md",
            "docs/getting-started.md",
            "docs/advanced.md",
        ],
        confidence_score=confidence,
        status="completed",
    )
    create_sample_questions_for_research(research)
    return research


def create_demo_data_for_issue(issue):
    """Create sample research, questions, and fix for an issue (used after Act or in seed)."""
    create_sample_research_for_issue(issue)
    create_sample_fix_for_issue(issue)
    issue.status = "fix_ready"
    issue.save(update_fields=["status"])
