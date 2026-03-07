import json
import subprocess
import tempfile
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

from .models import GitHubInstallation
from .services import create_installation_token, get_installation_repo
from agent.agents.understanding import default_understanding


def _get_tree_from_clone(owner, repo_name, installation_id):
    """Clone repo and return tree text (git ls-files or tree --fromfile)."""
    token = create_installation_token(installation_id)
    repo_url = f"https://x-access-token:{token}@github.com/{owner}/{repo_name}.git"
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, tmpdir],
            check=True,
            capture_output=True,
            timeout=120,
        )
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        result.check_returncode()
        tree_input = result.stdout
        try:
            tree_result = subprocess.run(
                ["tree", "--fromfile", "-"],
                cwd=tmpdir,
                input=tree_input,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if tree_result.returncode == 0 and tree_result.stdout:
                return tree_result.stdout
        except (FileNotFoundError, subprocess.SubprocessError):
            pass
        return tree_input


@method_decorator(csrf_exempt, name="dispatch")
class GitHubWebhookView(View):
    """POST /api/github/webhook - handle installation.created."""

    def post(self, request):
        event = request.headers.get("X-GitHub-Event", "")
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        # Smee (and some proxies) wrap the delivery as {"event": "...", "payload": {...}}
        payload = body.get("payload", body) if isinstance(body, dict) and "payload" in body else body
        if not isinstance(payload, dict):
            return HttpResponseBadRequest("Invalid payload")

        if event == "installation" or (isinstance(body, dict) and body.get("event") == "installation"):
            action = payload.get("action")
            if action == "created" or action == "added":
                installation = payload.get("installation") or {}
                installation_id = installation.get("id")
                if not installation_id:
                    return HttpResponseBadRequest("Missing installation id")

                repos = payload.get("repositories") or installation.get("repositories") or []
                if repos:
                    repo = repos[0]
                    repository_name = repo.get("name", "")
                    owner = (repo.get("owner") or {}).get("login", "") if isinstance(repo.get("owner"), dict) else ""
                    if not owner and repo.get("full_name"):
                        # e.g. "VaarunSinha/kapa-agent"
                        owner = repo.get("full_name", "").split("/")[0]
                    if not owner:
                        owner = (installation.get("account") or {}).get("login", "")
                else:
                    repository_name = ""
                    owner = (installation.get("account") or {}).get("login", "")

                inst, _ = GitHubInstallation.objects.update_or_create(
                    installation_id=installation_id,
                    defaults={
                        "repository_name": repository_name,
                        "owner": owner,
                    },
                )
                if not (inst.understanding or "").strip():
                    inst.understanding = default_understanding(owner, repository_name)
                    inst.save(update_fields=["understanding"])
        return HttpResponse(status=204)


def _setup_redirect(error, installation_id=None):
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
    qs = f"error={error}"
    if installation_id is not None:
        qs += f"&installation_id={installation_id}"
    return HttpResponseRedirect(f"{frontend_url}/github/setup?{qs}")


@require_http_methods(["GET"])
def github_setup_view(request):
    """
    GET /github/setup - after GitHub redirect. installation_id in query.
    Clone repo, generate tree, run mock understanding agent, save, redirect to frontend.
    """
    installation_id_raw = request.GET.get("installation_id")
    if not installation_id_raw:
        return _setup_redirect("missing_installation_id")

    try:
        installation_id = int(installation_id_raw)
    except ValueError:
        return _setup_redirect("invalid_installation_id", installation_id_raw)

    try:
        inst = GitHubInstallation.objects.get(installation_id=installation_id)
    except GitHubInstallation.DoesNotExist:
        # Redirect from GitHub often hits us before the installation.created webhook is
        # delivered, so the record may not exist yet. Create it from the GitHub API.
        owner, repo_name = get_installation_repo(installation_id)
        if not owner or not repo_name:
            return _setup_redirect("installation_not_found", installation_id)
        inst = GitHubInstallation.objects.create(
            installation_id=installation_id,
            owner=owner,
            repository_name=repo_name,
            understanding=default_understanding(owner, repo_name),
        )

    owner = inst.owner
    repo_name = inst.repository_name
    if not owner or not repo_name:
        return _setup_redirect("no_repository", installation_id)

    try:
        tree_text = _get_tree_from_clone(owner, repo_name, installation_id)
    except Exception:
        return _setup_redirect("clone_failed", installation_id)

    from agent.agents.understanding import generate_understanding
    inst.understanding = generate_understanding(tree_text)
    inst.raw_tree = tree_text
    inst.save(update_fields=["understanding", "raw_tree"])

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
    return HttpResponseRedirect(f"{frontend_url}/github/setup?installation_id={installation_id}&done=1")


# --- API for frontend: get/update installation (understanding) ---
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class GitHubInstallationAPIView(APIView):
    """
    GET /api/github/installation - return current installation and understanding.
    PATCH /api/github/installation - update understanding. Body: { "understanding": "..." } or { "installation_id": 123 } for GET.
    """

    def get(self, request):
        installation_id = request.query_params.get("installation_id")
        if installation_id:
            try:
                inst = GitHubInstallation.objects.get(installation_id=int(installation_id))
            except (GitHubInstallation.DoesNotExist, ValueError):
                return Response({"detail": "Installation not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            inst = GitHubInstallation.objects.order_by("-installed_at").first()
            if not inst:
                return Response({"detail": "No installation found."}, status=status.HTTP_404_NOT_FOUND)
        understanding = inst.understanding or default_understanding(inst.owner or "", inst.repository_name or "")
        return Response({
            "installation_id": inst.installation_id,
            "owner": inst.owner,
            "repository_name": inst.repository_name,
            "installed_at": inst.installed_at.isoformat() if inst.installed_at else None,
            "understanding": understanding,
        })

    def patch(self, request):
        installation_id = request.data.get("installation_id") or request.query_params.get("installation_id")
        understanding = request.data.get("understanding")
        if understanding is None:
            return Response({"detail": "understanding is required."}, status=status.HTTP_400_BAD_REQUEST)
        if installation_id:
            try:
                inst = GitHubInstallation.objects.get(installation_id=int(installation_id))
            except (GitHubInstallation.DoesNotExist, ValueError):
                return Response({"detail": "Installation not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            inst = GitHubInstallation.objects.order_by("-installed_at").first()
            if not inst:
                return Response({"detail": "No installation found."}, status=status.HTTP_404_NOT_FOUND)
        inst.understanding = understanding
        inst.save(update_fields=["understanding"])
        return Response({
            "installation_id": inst.installation_id,
            "understanding": inst.understanding,
        })
