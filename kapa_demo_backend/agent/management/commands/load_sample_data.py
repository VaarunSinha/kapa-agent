"""
Load sample coverage gaps aligned with intentional documentation gaps.
Use for demo: Coverage Gap → Issue → Research → Questions → Fix → Review → PR.

  python manage.py load_sample_data
  python manage.py load_sample_data --clear   # Reset all demo data including GitHub installations
"""
from django.core.management.base import BaseCommand
from data.models import CoverageGap
from agent.models import Issue, Fix, Question, Research


# Five coverage gaps matching the intentional docs gaps (exact title/finding/suggestion)
COVERAGE_GAPS = [
    {
        "title": "Research pipeline retrieval logic",
        "conversation_count": 12,
        "finding": "Users asked how the system determines which documentation files are relevant during research. The documentation mentions a research agent but does not explain how retrieval works.",
        "suggestion": "Document the vector retrieval process and how LlamaIndex is used to select documentation chunks.",
        "status": "open",
    },
    {
        "title": "Documentation style alignment",
        "conversation_count": 10,
        "finding": "Users asked how the system ensures generated documentation matches the project's writing style. The docs mention a style guide but do not explain how it is derived.",
        "suggestion": "Explain how the system extracts style patterns from existing documentation and generates style.md.",
        "status": "open",
    },
    {
        "title": "GitHub App authentication flow",
        "conversation_count": 8,
        "finding": "Users asked how the backend authenticates with GitHub when creating issues and pull requests. The documentation references a GitHub App but does not describe the authentication mechanism.",
        "suggestion": "Add documentation describing the GitHub App JWT flow and installation tokens.",
        "status": "open",
    },
    {
        "title": "Fix assistant editing workflow",
        "conversation_count": 14,
        "finding": "Users asked how fixes can be edited through the chat interface. The documentation mentions a Fix Assistant but does not explain how edits are applied.",
        "suggestion": "Document the fix editing endpoint and how semantic edits update documentation patches.",
        "status": "open",
    },
    {
        "title": "Handling multi-file documentation fixes",
        "conversation_count": 9,
        "finding": "Users asked how documentation fixes that affect multiple files are applied. The documentation references fixes but does not explain multi-file change handling.",
        "suggestion": "Document how fixes group multiple file updates and how commits are generated.",
        "status": "open",
    },
]


class Command(BaseCommand):
    help = "Load five coverage gaps aligned with docs gaps. Use --clear to reset all demo data (including GitHub installations)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete CoverageGap, Issue, Research, Question, Fix, and GitHubInstallation; then exit.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_all()
            return

        self.stdout.write("Clearing existing coverage gaps...")
        CoverageGap.objects.all().delete()

        for g in COVERAGE_GAPS:
            CoverageGap.objects.create(
                title=g["title"],
                conversation_count=g["conversation_count"],
                finding=g["finding"],
                suggestion=g["suggestion"],
                status=g["status"],
            )
            self.stdout.write(f"  Created coverage gap: {g['title']}")

        self.stdout.write(self.style.SUCCESS("Sample data loaded. Five open coverage gaps ready for demo."))

    def _clear_all(self):
        """Delete in dependency order: Fix → Question → Research → Issue → CoverageGap → GitHubInstallation."""
        self.stdout.write("Clearing existing data...")
        Fix.objects.all().delete()
        Question.objects.all().delete()
        Research.objects.all().delete()
        Issue.objects.all().delete()
        CoverageGap.objects.all().delete()
        try:
            from github.models import GitHubInstallation
            GitHubInstallation.objects.all().delete()
        except Exception:
            pass
        self.stdout.write(self.style.SUCCESS("Cleared. Run load_sample_data without --clear to load coverage gaps."))
