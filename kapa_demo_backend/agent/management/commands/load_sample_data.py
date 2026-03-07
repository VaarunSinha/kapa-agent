"""
Load mock/test data: coverage gaps + one acted gap with issue, research, questions, fix.
No workflow or API calls—just seeds the DB so you can test the UI.

After resetting DB:
  rm db.sqlite3
  python manage.py migrate
  python manage.py load_sample_data
"""
from django.core.management.base import BaseCommand
from data.models import CoverageGap
from agent.models import Issue, Fix, Question, Research
from agent.demo_data import create_demo_data_for_issue


class Command(BaseCommand):
    help = "Load mock data: coverage gaps and one acted gap with issue, research, questions, fix."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing agent + coverage gap data before loading.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Fix.objects.all().delete()
            Question.objects.all().delete()
            Research.objects.all().delete()
            Issue.objects.all().delete()
            CoverageGap.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared."))

        # Open coverage gaps (user can click Act on these)
        open_gaps = [
            {
                "title": "Installation steps not documented",
                "conversation_count": 12,
                "finding": "Users frequently ask 'How do I install the CLI?' but the docs jump straight to usage.",
                "suggestion": "Add a short 'Installation' section with npm and global install options.",
                "status": "open",
            },
            {
                "title": "API rate limits unclear",
                "conversation_count": 8,
                "finding": "Conversations show confusion about rate limits and 429 responses.",
                "suggestion": "Document rate limits and retry behavior in the API reference.",
                "status": "open",
            },
        ]
        for g in open_gaps:
            gap, created = CoverageGap.objects.get_or_create(
                title=g["title"],
                defaults={
                    "conversation_count": g["conversation_count"],
                    "finding": g["finding"],
                    "suggestion": g["suggestion"],
                    "status": g["status"],
                },
            )
            if created:
                self.stdout.write(f"  Created coverage gap: {gap.title}")

        # One acted gap with full mock: issue + research + questions + fix (multi-file)
        acted_gap_data = {
            "title": "Webhook payload schema missing",
            "conversation_count": 5,
            "finding": "Users ask for webhook payload examples; only high-level description exists.",
            "suggestion": "Add a 'Payload schema' subsection with a sample JSON body.",
            "status": "acted",
        }
        acted_gap, gap_created = CoverageGap.objects.get_or_create(
            title=acted_gap_data["title"],
            defaults={
                "conversation_count": acted_gap_data["conversation_count"],
                "finding": acted_gap_data["finding"],
                "suggestion": acted_gap_data["suggestion"],
                "status": acted_gap_data["status"],
            },
        )
        if gap_created:
            self.stdout.write(f"  Created acted gap: {acted_gap.title}")

        existing_issue = Issue.objects.filter(coverage_gap=acted_gap).first()
        if not existing_issue:
            issue = Issue.objects.create(
                coverage_gap=acted_gap,
                title=acted_gap.title,
                description=acted_gap.finding or "",
                status="fix_proposed",
            )
            self.stdout.write(f"  Created issue: {issue.title}")
            create_demo_data_for_issue(issue)
            self.stdout.write("  Added research, questions, and fix (multi-file mock).")
        else:
            self.stdout.write("  Acted gap already has an issue; skipping.")

        self.stdout.write(self.style.SUCCESS("Mock data loaded. Run the app and test the dashboard, issues, fixes."))
