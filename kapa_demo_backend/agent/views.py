import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView

logger = logging.getLogger(__name__)

from data.models import CoverageGap
from .models import Issue, Research, Question, Fix
from .tasks import create_issue_task, research_issue_task, publish_fixes_task, _get_repo_for_issue
from .serializers import (
    IssueSerializer,
    ResearchSerializer,
    ResearchListSerializer,
    QuestionSerializer,
    FixSerializer,
    FixListSerializer,
    FixDetailSerializer,
)


class CoverageGapActAPIView(APIView):
    """POST /api/coverage-gaps/<id>/act — create an Issue from the CoverageGap."""

    def post(self, request, id):
        try:
            gap = CoverageGap.objects.get(pk=id)
        except CoverageGap.DoesNotExist:
            return Response(
                {"detail": "Coverage gap not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        issue = Issue.objects.create(
            coverage_gap=gap,
            title=gap.title,
            description=gap.finding or "",
            status="created",
        )
        gap.status = "acted"
        gap.save(update_fields=["status"])
        create_issue_task.delay(str(issue.id))
        return Response({"issue_id": str(issue.id)}, status=status.HTTP_201_CREATED)


class IssueListAPIView(ListAPIView):
    """GET /api/issues — list all issues."""

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer


class IssueDetailAPIView(RetrieveAPIView):
    """GET /api/issues/<id> — issue detail."""

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    lookup_url_kwarg = "id"
    lookup_field = "id"


class ResearchListAPIView(ListAPIView):
    """GET /api/research — list all research tasks."""

    queryset = Research.objects.select_related("issue").all().order_by("-created_at")
    serializer_class = ResearchListSerializer


class ResearchByIssueAPIView(APIView):
    """GET /api/research/<issue_id> — list research for the issue."""

    def get(self, request, issue_id):
        research = Research.objects.filter(issue_id=issue_id).order_by("-created_at")
        serializer = ResearchSerializer(research, many=True)
        data = serializer.data
        return Response(data[0] if data else None)


class QuestionsByResearchAPIView(APIView):
    """GET /api/questions/<research_id> — list questions for the research."""

    def get(self, request, research_id):
        questions = Question.objects.filter(research_id=research_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response({
            "research_id": str(research_id),
            "questions": serializer.data,
        })


class QuestionsSubmitAPIView(APIView):
    """POST /api/questions/submit — save answers. Body: {"research_id": "uuid", "answers": [...]} or answers as dict keyed by question id. After save, re-queues research_issue_task."""

    def post(self, request):
        raw = request.data.get("answers")
        if raw is None:
            return Response(
                {"detail": "Expected 'answers'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if isinstance(raw, dict):
            answers = [{"question_id": k, "answer": v} for k, v in raw.items()]
        elif isinstance(raw, list):
            answers = raw
        else:
            return Response(
                {"detail": "Expected 'answers' as a list or object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        errors = []
        for i, item in enumerate(answers):
            if not isinstance(item, dict):
                errors.append({"index": i, "detail": "Each item must be an object."})
                continue
            qid = item.get("question_id")
            answer = item.get("answer")
            if not qid:
                errors.append({"question_id": None, "detail": "question_id is required."})
                continue
            try:
                question = Question.objects.get(pk=qid)
            except (Question.DoesNotExist, ValueError):
                errors.append({"question_id": str(qid), "detail": "Question not found."})
                continue
            question.answer = answer if answer is not None else ""
            question.save(update_fields=["answer"])

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        research_id = request.data.get("research_id")
        if research_id:
            try:
                research = Research.objects.get(pk=research_id)
                research_issue_task.delay(str(research.issue_id))
            except (Research.DoesNotExist, ValueError):
                pass
        return Response({"status": "ok"})


class FixListAPIView(ListAPIView):
    """GET /api/fixes — list all fixes."""

    queryset = Fix.objects.select_related("issue").all().order_by("-created_at")
    serializer_class = FixListSerializer


class FixDetailAPIView(APIView):
    """GET /api/fixes/<id> — single fix by fix id, or first fix for issue if id is issue_id."""

    def get(self, request, id):
        fix = Fix.objects.filter(pk=id).select_related("issue").first()
        if fix:
            serializer = FixDetailSerializer(fix)
            return Response(serializer.data)
        fix = Fix.objects.filter(issue_id=id).select_related("issue").first()
        if fix:
            serializer = FixDetailSerializer(fix)
            return Response(serializer.data)
        return Response(
            {"detail": "Fix not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


class FixesByIssueAPIView(APIView):
    """GET /api/fixes/by-issue/<issue_id> — list fixes for the issue."""

    def get(self, request, issue_id):
        fixes = Fix.objects.filter(issue_id=issue_id).order_by("-created_at")
        serializer = FixListSerializer(fixes, many=True)
        return Response(serializer.data)


class FixApproveAPIView(APIView):
    """POST /api/fixes/<id>/approve — set fix approved and trigger publish_fixes_task."""

    def post(self, request, id):
        try:
            fix = Fix.objects.get(pk=id)
        except Fix.DoesNotExist:
            return Response({"detail": "Fix not found."}, status=status.HTTP_404_NOT_FOUND)
        fix.status = "approved"
        fix.save(update_fields=["status"])
        publish_fixes_task.delay(str(fix.id))
        return Response({"status": "ok", "fix_id": str(fix.id)})


def _mock_chat_edit_files(files: list, message: str) -> list:
    """Mock: apply user message to fix files (e.g. append a line). Returns updated list of {path, content}."""
    if not files:
        return [{"path": "docs/update.md", "content": f"# Update\n\nBased on your request: {message[:200]}\n"}]
    updated = []
    for f in files:
        path = f.get("path", "")
        content = f.get("content", "")
        extra = f"\n\n<!-- Applied: {message[:80]} -->"
        updated.append({"path": path, "content": content + extra})
    return updated


class FixChatAPIView(APIView):
    """POST /api/fixes/<id>/chat — mock edit fix from user message; update Fix.files, return updated files.
    If fix is already published (PR exists), push a new commit to the same branch."""

    def post(self, request, id):
        try:
            fix = Fix.objects.select_related("issue").get(pk=id)
        except Fix.DoesNotExist:
            return Response({"detail": "Fix not found."}, status=status.HTTP_404_NOT_FOUND)
        message = (request.data.get("message") or "").strip()
        files = fix.files if fix.files else []
        if not files and fix.file_path:
            files = [{"path": fix.file_path, "content": fix.patch or ""}]
        updated_files = _mock_chat_edit_files(files, message or "No message")
        fix.files = updated_files
        fix.save(update_fields=["files"])
        if fix.status == "published" and fix.branch_name:
            installation_id, repo = _get_repo_for_issue(fix.issue)
            if installation_id and repo:
                try:
                    from github import services as github_services
                    github_services.commit_multiple_files(
                        installation_id, repo, fix.branch_name, {"files": updated_files}
                    )
                    logger.info(
                        "Fix chat: pushed extra commit to branch %s for fix %s",
                        fix.branch_name,
                        id,
                    )
                except Exception as e:
                    logger.exception(
                        "Fix chat: failed to push extra commit for fix %s: %s",
                        id,
                        e,
                    )
        out = [
            {"file_path": f.get("path", ""), "diff": f.get("content", ""), "markdown": f.get("content")}
            for f in updated_files
        ]
        return Response({"files": out})
