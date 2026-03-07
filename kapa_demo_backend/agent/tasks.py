import logging
from celery import shared_task
from django.db import transaction

from agent.agents.researcher import run_researcher

logger = logging.getLogger(__name__)
from agent.agents.writer import run_writer
from agent.models import Issue, Research, Question, Fix
from github.models import GitHubInstallation
from github import services as github_services


def _get_repo_for_issue(issue):
    """Get (installation_id, repo) for the issue's context; use first installation and repo."""
    inst = GitHubInstallation.objects.order_by("-installed_at").first()
    if not inst or not inst.owner or not inst.repository_name:
        return None, None
    return inst.installation_id, f"{inst.owner}/{inst.repository_name}"


@shared_task
def create_issue_task(issue_id: str):
    """Create GitHub issue, set status to researching, queue research_issue_task."""
    issue = Issue.objects.get(pk=issue_id)
    installation_id, repo = _get_repo_for_issue(issue)
    if not installation_id or not repo:
        logger.warning(
            "create_issue_task: no GitHub installation/repo; skipping GitHub issue creation for issue %s",
            issue_id,
        )
    else:
        try:
            github_services.create_issue(installation_id, repo, issue.title, issue.description)
            logger.info("Created GitHub issue for issue_id=%s repo=%s", issue_id, repo)
        except Exception as e:
            logger.exception(
                "create_issue_task: GitHub create_issue failed for issue %s: %s",
                issue_id,
                e,
            )
    issue.status = "researching"
    issue.save(update_fields=["status"])
    research_issue_task.delay(issue_id)


@shared_task
def research_issue_task(issue_id: str):
    """
    Run mock researcher. If questions: create Questions, set questions_pending, stop.
    If research: create Research, set research_complete, queue generate_fixes_task.
    If issue is already questions_pending (re-run after submit): build summary from answers, then generate_fixes.
    """
    issue = Issue.objects.get(pk=issue_id)

    if issue.status == "questions_pending":
        research = Research.objects.filter(issue=issue).order_by("-created_at").first()
        if research:
            answers = list(research.questions.values_list("question_text", "answer"))
            summary = "User answers: " + "; ".join(f"{q[:30]}: {a or '-'}" for q, a in answers)
            research.summary = summary
            research.status = "completed"
            research.save(update_fields=["summary", "status"])
        else:
            summary = "No research or answers."
        issue.status = "research_complete"
        issue.save(update_fields=["status"])
        generate_fixes_task.delay(issue_id)
        return

    _, repo = _get_repo_for_issue(issue)
    tree_text = ""
    if repo:
        inst = GitHubInstallation.objects.order_by("-installed_at").first()
        if inst:
            tree_text = (getattr(inst, "raw_tree", None) or "") or (inst.understanding or "")[:4000]
    result = run_researcher(issue.title, issue.description, tree_text)

    if result.get("action") == "questions":
        with transaction.atomic():
            research = Research.objects.create(
                issue=issue,
                summary="",
                status="completed",
            )
            for q in result.get("questions", []):
                Question.objects.create(
                    research=research,
                    question_text=q.get("question_text", ""),
                    question_type=q.get("question_type", "text"),
                    choices=q.get("choices"),
                )
            issue.status = "questions_pending"
            issue.save(update_fields=["status"])
        return

    # research
    summary = result.get("summary", "")
    with transaction.atomic():
        Research.objects.filter(issue=issue).update(summary=summary, status="completed")
        research = Research.objects.filter(issue=issue).order_by("-created_at").first()
        if not research:
            research = Research.objects.create(issue=issue, summary=summary, status="completed")
        else:
            research.summary = summary
            research.status = "completed"
            research.save(update_fields=["summary", "status"])
        issue.status = "research_complete"
        issue.save(update_fields=["status"])
    generate_fixes_task.delay(issue_id)


def _tree_lines_to_doc_paths(tree_text: str):
    """Extract list of file paths from tree text; return doc-like paths (.md or under docs/)."""
    if not (tree_text or "").strip():
        return []
    import re
    lines = []
    raw = (tree_text or "").strip()
    code_block = re.search(r"```\s*\n(.*?)```", raw, re.DOTALL)
    if code_block:
        raw = code_block.group(1)
    for line in raw.splitlines():
        path = line.strip().strip("/")
        if not path or path.startswith("#"):
            continue
        if path.endswith(".md") or "docs" in path.lower():
            lines.append(path)
    return lines[:50]


@shared_task
def generate_fixes_task(issue_id: str):
    """Run mock writer, create Fix records with files, set issue to fix_proposed."""
    issue = Issue.objects.get(pk=issue_id)
    research = Research.objects.filter(issue=issue).order_by("-created_at").first()
    summary = research.summary if research else ""
    installation_id, repo = _get_repo_for_issue(issue)
    file_path = None
    file_content = None
    if installation_id and repo:
        inst = GitHubInstallation.objects.order_by("-installed_at").first()
        tree_text = (getattr(inst, "raw_tree", None) or "") if inst else ""
        if not tree_text and inst and inst.understanding:
            tree_text = inst.understanding
        doc_paths = _tree_lines_to_doc_paths(tree_text)
        for path in doc_paths:
            if path.endswith(".md"):
                content, err = github_services.get_file_content(installation_id, repo, path)
                if content is not None and err is None:
                    file_path = path
                    file_content = content
                    break
    fix_payloads = run_writer(summary, issue.title, file_path=file_path, file_content=file_content)
    with transaction.atomic():
        for payload in fix_payloads:
            Fix.objects.create(
                issue=issue,
                summary=payload.get("summary", ""),
                files=payload.get("files", []),
                status="draft",
            )
        issue.status = "fix_proposed"
        issue.save(update_fields=["status"])


@shared_task
def publish_fixes_task(fix_id: str):
    """Create branch, commit files, open PR; set Fix to published, Issue to completed."""
    fix = Fix.objects.select_related("issue").get(pk=fix_id)
    issue = fix.issue
    installation_id, repo = _get_repo_for_issue(issue)
    if not installation_id or not repo:
        logger.warning(
            "publish_fixes_task: no GitHub installation/repo for fix %s; skipping branch/PR",
            fix_id,
        )
        fix.status = "published"
        fix.save(update_fields=["status"])
        issue.status = "completed"
        issue.save(update_fields=["status"])
        return
    branch_name = f"fix-{issue.id}"[:100]
    files = fix.files if fix.files else []
    if not files and fix.file_path:
        files = [{"path": fix.file_path, "content": fix.patch or ""}]
    if not files:
        logger.warning(
            "publish_fixes_task: no files on fix %s; skipping branch/PR",
            fix_id,
        )
        fix.status = "published"
        fix.save(update_fields=["status"])
        issue.status = "completed"
        issue.save(update_fields=["status"])
        return
    try:
        ref_data = github_services.create_branch(installation_id, repo, branch_name)
        base_commit_sha = (ref_data or {}).get("object", {}).get("sha")
        github_services.commit_multiple_files(
            installation_id, repo, branch_name, {"files": files}, base_commit_sha=base_commit_sha
        )
        pr_resp = github_services.create_pull_request(
            installation_id, repo, branch_name,
            title=f"Docs: {issue.title}",
            body=fix.summary or "",
        )
        fix.branch_name = branch_name
        fix.pr_url = pr_resp.get("html_url") or pr_resp.get("url") or None
        logger.info(
            "publish_fixes_task: created PR for fix %s: %s",
            fix_id,
            fix.pr_url,
        )
    except Exception as e:
        logger.exception(
            "publish_fixes_task: GitHub API failed for fix %s (branch/commit/PR): %s",
            fix_id,
            e,
        )
    fix.status = "published"
    fix.save(update_fields=["status", "branch_name", "pr_url"])
    issue.status = "completed"
    issue.save(update_fields=["status"])
