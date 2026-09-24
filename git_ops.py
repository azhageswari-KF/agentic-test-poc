"""
Thin wrapper around the GitHub REST API for what Creator's publish step
needs: create a branch off main, write a file to it, open a PR. No PyGithub
dependency -- just requests, so it's easy to see exactly what's being sent.

Auth: expects a token with repo-scoped write access (from a GitHub App
install token or a scoped fine-grained PAT -- see the access-model
discussion earlier). Never hardcode the token; it's read from the
environment only.
"""

import base64
import requests

API_ROOT = "https://api.github.com"


class GitHubError(Exception):
    pass


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _check(resp: requests.Response, action: str):
    if resp.status_code >= 300:
        raise GitHubError(f"{action} failed [{resp.status_code}]: {resp.text[:500]}")


def get_branch_sha(owner: str, repo: str, branch: str, token: str) -> str:
    url = f"{API_ROOT}/repos/{owner}/{repo}/git/ref/heads/{branch}"
    resp = requests.get(url, headers=_headers(token))
    _check(resp, f"get ref for {branch}")
    return resp.json()["object"]["sha"]


def create_branch(owner: str, repo: str, new_branch: str, base_sha: str, token: str) -> None:
    url = f"{API_ROOT}/repos/{owner}/{repo}/git/refs"
    payload = {"ref": f"refs/heads/{new_branch}", "sha": base_sha}
    resp = requests.post(url, headers=_headers(token), json=payload)
    if resp.status_code == 422 and "already exists" in resp.text:
        return  # branch already there (e.g. rerun) -- fine, we'll just update the file on it
    _check(resp, f"create branch {new_branch}")


def _get_existing_file_sha(owner: str, repo: str, branch: str, path: str, token: str):
    url = f"{API_ROOT}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=_headers(token), params={"ref": branch})
    if resp.status_code == 200:
        return resp.json()["sha"]
    return None  # file doesn't exist yet on this branch


def upsert_file(owner: str, repo: str, branch: str, path: str, content: str, message: str, token: str) -> str:
    """Creates or updates a file on the given branch. Returns the commit SHA."""
    url = f"{API_ROOT}/repos/{owner}/{repo}/contents/{path}"
    existing_sha = _get_existing_file_sha(owner, repo, branch, path, token)

    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": branch,
    }
    if existing_sha:
        payload["sha"] = existing_sha

    resp = requests.put(url, headers=_headers(token), json=payload)
    _check(resp, f"write {path} to {branch}")
    return resp.json()["commit"]["sha"]


def open_pull_request(owner: str, repo: str, head_branch: str, base_branch: str, title: str, body: str, token: str) -> str:
    """Returns the PR's HTML URL. Requires the token identity to NOT also
    be set as a reviewer -- GitHub blocks self-approval, which is exactly
    the guardrail we want (agent opens, a human approves)."""
    url = f"{API_ROOT}/repos/{owner}/{repo}/pulls"
    payload = {"title": title, "head": head_branch, "base": base_branch, "body": body}
    resp = requests.post(url, headers=_headers(token), json=payload)
    if resp.status_code == 422 and "already exists" in resp.text:
        # PR already open for this branch -- fetch and return its URL instead of erroring
        list_resp = requests.get(url, headers=_headers(token), params={"head": f"{owner}:{head_branch}"})
        _check(list_resp, "list existing PRs")
        prs = list_resp.json()
        if prs:
            return prs[0]["html_url"]
    _check(resp, "open pull request")
    return resp.json()["html_url"]
