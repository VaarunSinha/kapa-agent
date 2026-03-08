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


@shared_task(bind=True, max_retries=3)
def research_issue_task(self, issue_id: str):
    """
    Run research agent. If questions: create Questions, set questions_pending. If research: create Research,
    set research_complete, queue generate_fixes_task. On final failure set research_failed.
    If issue is questions_pending (re-run after submit): build summary from answers, then generate_fixes.
    """
    try:
        issue = Issue.objects.get(pk=issue_id)
    except Issue.DoesNotExist:
        logger.warning("research_issue_task: issue %s not found", issue_id)
        return

    if issue.status == "questions_pending":
        research = Research.objects.filter(issue=issue).order_by("-created_at").first()
        if not research:
            issue.status = "research_failed"
            issue.save(update_fields=["status"])
            return
        answers = list(research.questions.values_list("question_text", "answer"))
        answers_summary = "User answers: " + "; ".join(f"{q[:30]}: {a or '-'}" for q, a in answers)
        installation_id, repo = _get_repo_for_issue(issue)
        tree_text = ""
        if repo:
            inst = GitHubInstallation.objects.order_by("-installed_at").first()
            if inst:
                tree_text = (getattr(inst, "raw_tree", None) or "") or (inst.understanding or "")[:4000]
        try:
            result = run_researcher(
                issue.title,
                issue.description,
                tree_text,
                retrieval_context="",
                installation_id=installation_id,
                research_goal=getattr(issue, "research_goal", "") or "",
                user_answers=answers_summary,
            )
        except Exception as e:
            logger.exception(
                "research_issue_task: researcher failed for issue %s (after answers): %s",
                issue_id,
                e,
            )
            if self.request.retries >= self.max_retries - 1:
                issue.status = "research_failed"
                issue.save(update_fields=["status"])
            else:
                raise self.retry(exc=e)
            return
        if result.get("action") == "error":
            logger.warning(
                "research_issue_task: researcher error for issue %s (after answers): %s",
                issue_id,
                result.get("error", "unknown"),
            )
            issue.status = "research_failed"
            issue.save(update_fields=["status"])
            return
        if result.get("action") == "questions":
            logger.warning(
                "research_issue_task: researcher returned questions despite user_answers for issue %s",
                issue_id,
            )
            issue.status = "research_failed"
            issue.save(update_fields=["status"])
            return
        summary = result.get("summary", "")
        files_referenced = result.get("files_referenced") or []
        file_to_edit = result.get("file_to_edit") or ""
        coverage_gap_description = result.get("coverage_gap_description") or ""
        recommended_changes = result.get("recommended_changes") or ""
        raw_conf = result.get("confidence_score")
        try:
            confidence_score = float(raw_conf) if raw_conf is not None else 0.75
            if not (0 <= confidence_score <= 1):
                confidence_score = 0.75
        except (TypeError, ValueError):
            confidence_score = 0.75
        research.summary = summary
        research.files_analyzed = files_referenced
        research.file_to_edit = file_to_edit
        research.coverage_gap_description = coverage_gap_description
        research.recommended_changes = recommended_changes
        research.confidence_score = confidence_score
        research.status = "completed"
        research.save(update_fields=["summary", "files_analyzed", "file_to_edit", "coverage_gap_description", "recommended_changes", "confidence_score", "status"])
        issue.status = "research_complete"
        issue.save(update_fields=["status"])
        generate_fixes_task.delay(issue_id)
        return

    installation_id, repo = _get_repo_for_issue(issue)
    tree_text = ""
    if repo:
        inst = GitHubInstallation.objects.order_by("-installed_at").first()
        if inst:
            tree_text = (getattr(inst, "raw_tree", None) or "") or (inst.understanding or "")[:4000]

    try:
        result = run_researcher(
            issue.title,
            issue.description,
            tree_text,
            retrieval_context="",
            installation_id=installation_id,
            research_goal=getattr(issue, "research_goal", "") or "",
        )
    except Exception as e:
        logger.exception("research_issue_task: researcher failed for issue %s: %s", issue_id, e)
        if self.request.retries >= self.max_retries - 1:
            issue.status = "research_failed"
            issue.save(update_fields=["status"])
        else:
            raise self.retry(exc=e)
        return

    if result.get("action") == "error":
        logger.warning(
            "research_issue_task: researcher error for issue %s: %s",
            issue_id,
            result.get("error", "unknown"),
        )
        issue.status = "research_failed"
        issue.save(update_fields=["status"])
        return

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

    summary = result.get("summary", "")
    files_referenced = result.get("files_referenced") or []
    file_to_edit = result.get("file_to_edit") or ""
    coverage_gap_description = result.get("coverage_gap_description") or ""
    recommended_changes = result.get("recommended_changes") or ""
    raw_conf = result.get("confidence_score")
    try:
        confidence_score = float(raw_conf) if raw_conf is not None else 0.75
        if not (0 <= confidence_score <= 1):
            confidence_score = 0.75
    except (TypeError, ValueError):
        confidence_score = 0.75
    with transaction.atomic():
        Research.objects.filter(issue=issue).update(
            summary=summary,
            files_analyzed=files_referenced,
            file_to_edit=file_to_edit,
            coverage_gap_description=coverage_gap_description,
            recommended_changes=recommended_changes,
            confidence_score=confidence_score,
            status="completed",
        )
        research = Research.objects.filter(issue=issue).order_by("-created_at").first()
        if not research:
            research = Research.objects.create(
                issue=issue,
                summary=summary,
                files_analyzed=files_referenced,
                file_to_edit=file_to_edit,
                coverage_gap_description=coverage_gap_description,
                recommended_changes=recommended_changes,
                confidence_score=confidence_score,
                status="completed",
            )
        else:
            research.summary = summary
            research.files_analyzed = files_referenced
            research.file_to_edit = file_to_edit
            research.coverage_gap_description = coverage_gap_description
            research.recommended_changes = recommended_changes
            research.confidence_score = confidence_score
            research.status = "completed"
            research.save(update_fields=["summary", "files_analyzed", "file_to_edit", "coverage_gap_description", "recommended_changes", "confidence_score", "status"])
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
    """Run writer agent (retrieval + style), create Fix records with files, set issue to fix_proposed."""
    issue = Issue.objects.get(pk=issue_id)
    research = Research.objects.filter(issue=issue).order_by("-created_at").first()
    if not research:
        logger.warning("generate_fixes_task: no research for issue %s; skipping", issue_id)
        return
    summary = research.summary or ""
    files_referenced = list(research.files_analyzed) if research.files_analyzed else []
    installation_id, repo = _get_repo_for_issue(issue)
    retrieval_context = ""
    style_md = ""
    if installation_id:
        from agent.retrieval import get_retrieval_context
        query = f"{issue.title} {summary}"[:500]
        retrieval_context = get_retrieval_context(installation_id, query)
        inst = GitHubInstallation.objects.order_by("-installed_at").first()
        if inst and getattr(inst, "style_md", None):
            style_md = inst.style_md or ""
    file_path = None
    file_content = None
    if installation_id and repo:
        inst = GitHubInstallation.objects.order_by("-installed_at").first()
        tree_text = (getattr(inst, "raw_tree", None) or "") if inst else ""
        if not tree_text and inst and inst.understanding:
            tree_text = inst.understanding
        doc_paths = _tree_lines_to_doc_paths(tree_text)
        # Use structured file_to_edit from research when set; else fall back to first doc in files_analyzed, then doc_paths
        if getattr(research, "file_to_edit", None) and isinstance(research.file_to_edit, str) and research.file_to_edit.strip():
            content, err = github_services.get_file_content(installation_id, repo, research.file_to_edit.strip())
            if content is not None and err is None:
                file_path = research.file_to_edit.strip()
                file_content = content
        if file_path is None:
            for path in (research.files_analyzed or []):
                if not path or not (isinstance(path, str) and (path.endswith(".md") or "docs" in path.lower())):
                    continue
                content, err = github_services.get_file_content(installation_id, repo, path)
                if content is not None and err is None:
                    file_path = path
                    file_content = content
                    break
        if file_path is None:
            for path in doc_paths:
                if path.endswith(".md"):
                    content, err = github_services.get_file_content(installation_id, repo, path)
                    if content is not None and err is None:
                        file_path = path
                        file_content = content
                        break
    coverage_gap_description = getattr(research, "coverage_gap_description", None) or ""
    recommended_changes = getattr(research, "recommended_changes", None) or ""
    fix_payloads = run_writer(
        summary,
        issue.title,
        file_path=file_path,
        file_content=file_content,
        retrieval_context=retrieval_context,
        style_md=style_md,
        files_referenced=files_referenced or None,
        coverage_gap_description=coverage_gap_description,
        recommended_changes=recommended_changes,
    )
    if not fix_payloads:
        logger.warning("generate_fixes_task: no fixes for issue %s", issue_id)
        return
    with transaction.atomic():
        for payload in fix_payloads:
            files = list(payload.get("files", []))
            # Build map of path -> original_content so every file gets a proper diff
            original_map = {}
            if file_path and file_content is not None:
                original_map[file_path] = file_content
            if installation_id and repo:
                for f in files:
                    p = f.get("path") or f.get("file_path") or ""
                    if p and p not in original_map:
                        content, err = github_services.get_file_content(
                            installation_id, repo, p
                        )
                        if content is not None and err is None:
                            original_map[p] = content
            for f in files:
                p = f.get("path") or f.get("file_path") or ""
                if p and original_map.get(p) is not None:
                    f["original_content"] = original_map[p]
            Fix.objects.create(
                issue=issue,
                summary=payload.get("summary", ""),
                files=files,
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
