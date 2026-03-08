from rest_framework import serializers
from .models import Issue, Research, Question, Fix
from .utils import unified_diff_string


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id",
            "coverage_gap",
            "title",
            "description",
            "research_goal",
            "status",
            "created_at",
            "updated_at",
        ]


class ResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = [
            "id",
            "issue",
            "summary",
            "files_analyzed",
            "confidence_score",
            "status",
            "created_at",
            "updated_at",
        ]


class ResearchListSerializer(serializers.ModelSerializer):
    issue_id = serializers.UUIDField(source="issue.id", read_only=True)
    issue_title = serializers.CharField(source="issue.title", read_only=True)

    class Meta:
        model = Research
        fields = [
            "id",
            "issue_id",
            "issue_title",
            "status",
            "confidence_score",
            "created_at",
        ]


def _question_type_for_frontend(question_type):
    if question_type == "choice":
        return "radiogroup"
    return question_type


class QuestionSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    title = serializers.CharField(source="question_text", read_only=True)

    class Meta:
        model = Question
        fields = ["id", "type", "title", "choices"]

    def get_type(self, obj):
        return _question_type_for_frontend(obj.question_type)


class FixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fix
        fields = [
            "id",
            "issue",
            "file_path",
            "patch",
            "summary",
            "status",
            "created_at",
            "updated_at",
        ]


class FixListSerializer(serializers.ModelSerializer):
    issue_id = serializers.UUIDField(source="issue.id", read_only=True)
    issue_title = serializers.CharField(source="issue.title", read_only=True)
    files_count = serializers.SerializerMethodField()

    class Meta:
        model = Fix
        fields = ["id", "issue_id", "issue_title", "status", "files_count", "created_at"]

    def get_files_count(self, obj):
        if obj.files:
            return len(obj.files)
        return 1 if obj.file_path else 0


class FixDetailSerializer(serializers.ModelSerializer):
    issue_id = serializers.UUIDField(source="issue.id", read_only=True)
    files = serializers.SerializerMethodField()

    class Meta:
        model = Fix
        fields = ["id", "issue_id", "status", "created_at", "files"]

    def get_files(self, obj):
        if obj.files:
            def content_to_diff(content):
                """Fallback: format raw content as unified-diff additions (backward compat when no original_content)."""
                if not content:
                    return ""
                lines = content.splitlines()
                return "\n".join("+ " + line for line in lines)

            result = []
            for f in obj.files:
                path = f.get("path", "")
                content = f.get("content", "")
                if f.get("original_content") is not None:
                    diff = unified_diff_string(f["original_content"], content, path)
                else:
                    diff = content_to_diff(content)
                result.append({
                    "file_path": path,
                    "diff": diff,
                    "markdown": content,
                })
            return result
        if obj.file_path:
            return [
                {
                    "file_path": obj.file_path,
                    "diff": obj.patch,
                    "markdown": None,
                }
            ]
        return []
