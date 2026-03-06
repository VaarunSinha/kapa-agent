from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import CoverageGap
from .serializers import CoverageGapSerializer


class CoverageGapListAPIView(APIView):
    """GET /api/coverage-gaps — returns metrics and list of coverage gaps."""

    def get(self, request):
        gaps = CoverageGap.objects.all()
        serializer = CoverageGapSerializer(gaps, many=True)

        # Placeholder; can be computed later (e.g. from analytics)
        conversations_processed = 226

        return Response(
            {
                "conversationsProcessed": conversations_processed,
                "coverageGapsIdentified": gaps.count(),
                "githubInstallUrl": getattr(
                    settings,
                    "GITHUB_INSTALL_URL",
                    "https://github.com/apps/demo-docs-agent/installations/new",
                ),
                "gaps": serializer.data,
            }
        )
