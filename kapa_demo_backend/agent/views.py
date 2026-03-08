import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView

logger = logging.getLogger(__name__)

# Fix Chat UI copy (exposed via API; do not hardcode in frontend)
FIX_CHAT_ASSISTANT_INTRO = (
    "Hi! I've reviewed the proposed documentation fix. Feel free to ask me to revise specific "
    "sections, change the tone, add examples, or restructure any part of it. The style guide is "
    "generated from excerpts of the related documentation (selected by the researcher), and the "
    "writer uses similar language and style."
)
FIX_CHAT_ASSISTANT_REPLY_SUCCESS = (
    "I've applied your changes. The Proposed Changes panel on the left has been updated."
)

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
from .utils import unified_diff_string


class CoverageGapActAPIView(APIView):
    """POST /api/coverage-gaps/<id>/act — create an Issue from the CoverageGap (Issue Creator agent)."""

    def post(self, request, id):
        try:
            gap = CoverageGap.objects.get(pk=id)
        except CoverageGap.DoesNotExist:
            return Response(
                {"detail": "Coverage gap not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from github.models import GitHubInstallation
        from agent.agents.issue_creator import create_issue_from_gap
        from agent.agents.understanding import default_understanding

        inst = GitHubInstallation.objects.order_by("-installed_at").first()
        understanding = (inst.understanding if inst else None) or default_understanding(
            inst.owner if inst else "", inst.repository_name if inst else ""
        )
        payload = create_issue_from_gap(
            gap_title=gap.title,
            gap_finding=gap.finding or "",
            gap_suggestion=gap.suggestion or "",
            understanding=understanding,
        )
        issue = Issue.objects.create(
            coverage_gap=gap,
            title=payload["title"],
            description=payload["description"],
            research_goal=payload.get("research_goal") or "",
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
            data = dict(serializer.data)
            data["assistant_intro"] = FIX_CHAT_ASSISTANT_INTRO
            data["assistant_reply_success"] = FIX_CHAT_ASSISTANT_REPLY_SUCCESS
            return Response(data)
        fix = Fix.objects.filter(issue_id=id).select_related("issue").first()
        if fix:
            serializer = FixDetailSerializer(fix)
            data = dict(serializer.data)
            data["assistant_intro"] = FIX_CHAT_ASSISTANT_INTRO
            data["assistant_reply_success"] = FIX_CHAT_ASSISTANT_REPLY_SUCCESS
            return Response(data)
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


class FixChatAPIView(APIView):
    """POST /api/fixes/<id>/chat — edit fix from user message (Fix Assistant + style.md); update Fix.files, return updated files.
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
        # Normalize keys but preserve original_content so fix assistant can use it
        files = [
            {
                "path": (f.get("path") or f.get("file_path") or ""),
                "content": (f.get("content") or f.get("diff") or f.get("patch") or ""),
                "original_content": f.get("original_content"),
            }
            for f in files
        ]
        style_md = ""
        inst = None
        try:
            from github.models import GitHubInstallation
            inst = GitHubInstallation.objects.order_by("-installed_at").first()
            if inst and getattr(inst, "style_md", None):
                style_md = inst.style_md or ""
        except Exception:
            pass
        from agent.agents.fix_assistant import apply_fix_instruction
        updated = apply_fix_instruction(files, message or "No message", style_md)
        if updated is None:
            logger.warning(
                "FixChatAPIView: apply_fix_instruction returned None for fix_id=%s message_len=%s",
                id,
                len(message or ""),
            )
            return Response(
                {"error": "LLM unavailable; could not apply instruction."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        updated_files = updated["files"]
        assistant_reply = (updated.get("assistant_message") or "").strip()
        # Preserve original_content when saving: merge LLM result with existing fix.files
        original_by_path = {
            (f.get("path") or f.get("file_path") or ""): f.get("original_content")
            for f in files
        }
        merged = []
        for f in updated_files:
            path = f.get("path") or ""
            merged.append({
                "path": path,
                "content": f.get("content") or "",
                "original_content": original_by_path.get(path),
            })
        fix.files = merged
        fix.save(update_fields=["files"])
        if fix.status == "published" and fix.branch_name:
            installation_id, repo = _get_repo_for_issue(fix.issue)
            if installation_id and repo:
                try:
                    from github import services as github_services
                    github_services.commit_multiple_files(
                        installation_id, repo, fix.branch_name, {"files": fix.files}
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
            {
                "file_path": f.get("path", ""),
                "diff": unified_diff_string(
                    f.get("original_content") if f.get("original_content") is not None else "",
                    f.get("content", ""),
                    f.get("path", ""),
                ),
                "markdown": f.get("content"),
            }
            for f in fix.files
        ]
        return Response({
            "files": out,
            "assistant_reply": assistant_reply,
        })
