"""
Real GitHub API integration using App installation tokens.
Requires GITHUB_APP_ID and GITHUB_PRIVATE_KEY in settings.
GITHUB_PRIVATE_KEY can be the PEM string, or a path (e.g. github.pem) relative to project root or absolute.
"""
import os
import time
from pathlib import Path

from django.conf import settings
import jwt
import requests


def _get_private_key():
    key = getattr(settings, "GITHUB_PRIVATE_KEY", "") or ""
    if not key:
        raise ValueError("GITHUB_PRIVATE_KEY is not set")
    if key.strip().startswith("-----"):
        return key
    # Resolve relative paths (e.g. "github.pem") against project root (directory containing manage.py)
    path = Path(key)
    if not path.is_absolute():
        base_dir = getattr(settings, "BASE_DIR", None)
        if base_dir is not None:
            path = Path(base_dir) / key
    try:
        return path.read_text()
    except OSError:
        return key


def _get_app_jwt():
    """Create a JWT for the GitHub App (valid 10 minutes)."""
    app_id = getattr(settings, "GITHUB_APP_ID", "") or ""
    if not app_id:
        raise ValueError("GITHUB_APP_ID is not set")
    private_key = _get_private_key()
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 600,
        "iss": str(app_id).strip(),
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def create_installation_token(installation_id):
    """
    Exchange app JWT for an installation access token (real GitHub API).
    Returns the token string; raises on API error.
    """
    api_version = getattr(settings, "GITHUB_API_VERSION", "2026-01-01")
    jwt_token = _get_app_jwt()
    if hasattr(jwt_token, "decode"):
        jwt_token = jwt_token.decode("utf-8")
    url = f"https://api.github.com/app/installations/{int(installation_id)}/access_tokens"
    resp = requests.post(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {jwt_token}",
            "X-GitHub-Api-Version": api_version,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data.get("token")
    if not token:
        raise ValueError("GitHub did not return an access token")
    return token


def _auth_headers(installation_id):
    token = create_installation_token(installation_id)
    api_version = getattr(settings, "GITHUB_API_VERSION", "2026-01-01")
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": api_version,
    }


def get_installation_repo(installation_id):
    """
    Fetch first repository for this installation (for setup when webhook didn't run).
    Returns (owner, repository_name) or (None, None) on failure.
    """
    try:
        token = create_installation_token(installation_id)
        api_version = getattr(settings, "GITHUB_API_VERSION", "2026-01-01")
        resp = requests.get(
            "https://api.github.com/installation/repositories",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": api_version,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        repos = data.get("repositories") or []
        if not repos:
            return None, None
        repo = repos[0]
        owner = repo.get("owner", {}).get("login", "")
        name = repo.get("name", "")
        return owner, name
    except Exception:
        return None, None


def get_file_content(installation_id, repo, path):
    """
    Fetch file content from repo. path is the file path (e.g. docs/README.md).
    Returns (content_str, None) on success, or (None, error) on 404/error.
    Uses GitHub Contents API; decodes base64.
    """
    import base64
    owner, repo_name = repo.split("/", 1)
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    try:
        resp = requests.get(
            url,
            headers=_auth_headers(installation_id),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("encoding") == "base64":
            return base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace"), None
        return data.get("content", ""), None
    except Exception as e:
        return None, e


def create_issue(installation_id, repo, title, body):
    """
    Create a GitHub issue. repo is "owner/repo_name".
    Real GitHub API.
    """
    owner, repo_name = repo.split("/", 1)
    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
    resp = requests.post(
        url,
        headers={**_auth_headers(installation_id), "Content-Type": "application/json"},
        json={"title": title, "body": body or ""},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _get_default_branch_sha(installation_id, repo):
    owner, repo_name = repo.split("/", 1)
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}",
        headers=_auth_headers(installation_id),
        timeout=30,
    )
    resp.raise_for_status()
    default_branch = resp.json().get("default_branch", "main")
    ref_url = f"https://api.github.com/repos/{owner}/{repo_name}/git/ref/heads/{default_branch}"
    ref_resp = requests.get(ref_url, headers=_auth_headers(installation_id), timeout=30)
    ref_resp.raise_for_status()
    commit_sha = ref_resp.json()["object"]["sha"]
    return default_branch, commit_sha


def create_branch(installation_id, repo, branch_name):
    """
    Create a new branch from default branch. Real GitHub API.
    Requires GitHub App permission: Contents (read and write).
    """
    owner, repo_name = repo.split("/", 1)
    default_branch, commit_sha = _get_default_branch_sha(installation_id, repo)
    url = f"https://api.github.com/repos/{owner}/{repo_name}/git/refs"
    resp = requests.post(
        url,
        headers={**_auth_headers(installation_id), "Content-Type": "application/json"},
        json={"ref": f"refs/heads/{branch_name}", "sha": commit_sha},
        timeout=30,
    )
    if resp.status_code == 403:
        raise PermissionError(
            "GitHub App needs 'Contents' permission with read and write access to create branches "
            "and push commits. In GitHub: App → Settings → Permissions & events → Repository permissions, "
            "set Contents to Read and write. Then re-install the app or accept new permissions."
        ) from None
    resp.raise_for_status()
    return resp.json()


def commit_multiple_files(installation_id, repo, branch, changes, base_commit_sha=None):
    """
    Commit multiple files in one commit on the given branch.
    changes: {"files": [{"path": "docs/a.md", "content": "..."}, ...]}
    Real GitHub API (create blobs, tree, commit, update ref).
    If base_commit_sha is provided (e.g. from create_branch response), skip GET ref to avoid 404
    right after creating the branch.
    """
    owner, repo_name = repo.split("/", 1)
    files = changes.get("files") if isinstance(changes, dict) else []
    if not files:
        raise ValueError("changes must include a non-empty 'files' list")

    headers = {**_auth_headers(installation_id), "Content-Type": "application/json"}
    # GET uses git/ref/..., PATCH uses git/refs/... (GitHub API difference)
    ref_url = f"https://api.github.com/repos/{owner}/{repo_name}/git/ref/heads/{branch}"
    refs_url = f"https://api.github.com/repos/{owner}/{repo_name}/git/refs/heads/{branch}"

    # Get current commit on branch (use provided sha when we just created the branch)
    if base_commit_sha:
        commit_sha = base_commit_sha
    else:
        ref_resp = requests.get(ref_url, headers=_auth_headers(installation_id), timeout=30)
        ref_resp.raise_for_status()
        commit_sha = ref_resp.json()["object"]["sha"]

    commit_resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/git/commits/{commit_sha}",
        headers=_auth_headers(installation_id),
        timeout=30,
    )
    commit_resp.raise_for_status()
    base_tree_sha = commit_resp.json()["tree"]["sha"]

    # Create blobs and build tree entries
    tree_entries = []
    for f in files:
        path = f.get("path") or ""
        content = f.get("content") or ""
        if not path:
            continue
        blob_resp = requests.post(
            f"https://api.github.com/repos/{owner}/{repo_name}/git/blobs",
            headers=headers,
            json={"content": content, "encoding": "utf-8"},
            timeout=30,
        )
        blob_resp.raise_for_status()
        blob_sha = blob_resp.json()["sha"]
        tree_entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob_sha})

    # Create tree
    tree_resp = requests.post(
        f"https://api.github.com/repos/{owner}/{repo_name}/git/trees",
        headers=headers,
        json={"base_tree": base_tree_sha, "tree": tree_entries},
        timeout=30,
    )
    tree_resp.raise_for_status()
    new_tree_sha = tree_resp.json()["sha"]

    # Create commit
    commit_create_resp = requests.post(
        f"https://api.github.com/repos/{owner}/{repo_name}/git/commits",
        headers=headers,
        json={
            "message": "docs: update documentation",
            "tree": new_tree_sha,
            "parents": [commit_sha],
        },
        timeout=30,
    )
    commit_create_resp.raise_for_status()
    new_commit_sha = commit_create_resp.json()["sha"]

    # Update ref (PATCH uses refs path, not ref)
    update_resp = requests.patch(
        refs_url,
        headers=headers,
        json={"sha": new_commit_sha},
        timeout=30,
    )
    update_resp.raise_for_status()
    return update_resp.json()


def create_pull_request(installation_id, repo, branch, title, body):
    """
    Open a PR from branch to default branch. Real GitHub API.
    """
    owner, repo_name = repo.split("/", 1)
    default_branch, _ = _get_default_branch_sha(installation_id, repo)
    url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    resp = requests.post(
        url,
        headers={**_auth_headers(installation_id), "Content-Type": "application/json"},
        json={
            "title": title,
            "body": body or "",
            "head": branch,
            "base": default_branch,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
