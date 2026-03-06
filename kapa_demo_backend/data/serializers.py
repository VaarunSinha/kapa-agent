from rest_framework import serializers
from .models import CoverageGap


class CoverageGapSerializer(serializers.ModelSerializer):
    """Serializer for CoverageGap with camelCase keys for API response."""

    conversationCount = serializers.IntegerField(source="conversation_count", read_only=True)

    class Meta:
        model = CoverageGap
        fields = [
            "id",
            "title",
            "conversationCount",
            "finding",
            "suggestion",
            "status",
        ]
