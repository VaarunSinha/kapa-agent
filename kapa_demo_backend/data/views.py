from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import CoverageGap
from .serializers import CoverageGapSerializer

try:
    from github.models import GitHubInstallation
except ImportError:
    GitHubInstallation = None


class CoverageGapListAPIView(APIView):
    """GET /api/coverage-gaps — returns metrics and list of coverage gaps."""

    def get(self, request):
        gaps = CoverageGap.objects.all()
        serializer = CoverageGapSerializer(gaps, many=True)

        # Placeholder; can be computed later (e.g. from analytics)
        conversations_processed = 226

        has_connected_repo = False
        connected_repo = None
        if GitHubInstallation is not None:
            has_connected_repo = GitHubInstallation.objects.exists()
            if has_connected_repo:
                inst = GitHubInstallation.objects.order_by("-installed_at").first()
                if inst:
                    connected_repo = {
                        "owner": inst.owner or "",
                        "repository_name": inst.repository_name or "",
                        "installation_id": inst.installation_id,
                    }

        return Response(
            {
                "conversationsProcessed": conversations_processed,
                "coverageGapsIdentified": gaps.count(),
                "githubInstallUrl": getattr(
                    settings,
                    "GITHUB_INSTALL_URL",
                    "https://github.com/apps/demo-docs-agent/installations/new",
                ),
                "hasConnectedRepo": has_connected_repo,
                "connectedRepo": connected_repo,
                "gaps": serializer.data,
            }
        )
