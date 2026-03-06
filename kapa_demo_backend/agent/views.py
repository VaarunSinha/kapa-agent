from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView

from data.models import CoverageGap
from .models import Issue, Research, Question, Fix
from .demo_data import create_demo_data_for_issue
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

        # Create sample research, questions, and fix so the new issue has demo data to view
        create_demo_data_for_issue(issue)

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
    """POST /api/questions/submit — save answers. Body: {"answers": [{"question_id": "uuid", "answer": "..."}, ...]} or {"answers": {"question-uuid": "value", ...}}."""

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
