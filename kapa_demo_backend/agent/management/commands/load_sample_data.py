"""
Load sample data for testing the docs workflow: coverage gaps, and one pre-acted
gap with issue, research, questions, and fix.

Usage:
  python manage.py load_sample_data
  python manage.py load_sample_data --clear   # delete existing sample data first
"""
from django.core.management.base import BaseCommand
from data.models import CoverageGap
from agent.models import Issue, Fix, Question, Research
from agent.demo_data import create_demo_data_for_issue


class Command(BaseCommand):
    help = "Load sample coverage gaps and one pre-acted gap with issue, research, questions, fix."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing agent + coverage gap data before loading (resets demo).",
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

        # Create open coverage gaps (user can click Act on these)
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

        # One acted gap with full issue + research + questions + fix (so list has data)
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

        # Create issue + research + questions + fix for the acted gap (if no issue exists yet)
        existing_issue = Issue.objects.filter(coverage_gap=acted_gap).first()
        if not existing_issue:
            issue = Issue.objects.create(
                coverage_gap=acted_gap,
                title=acted_gap.title,
                description=acted_gap.finding or "",
                status="created",
            )
            self.stdout.write(f"  Created issue: {issue.title}")
            create_demo_data_for_issue(issue)
            self.stdout.write("  Added research, questions, and fix for that issue.")
        else:
            self.stdout.write("  Acted gap already has an issue; skipping.")

        self.stdout.write(self.style.SUCCESS("Sample data loaded. Open the dashboard and click Act on a gap to create an issue with research, questions, and a fix."))
