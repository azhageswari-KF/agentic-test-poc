"""
Alternative Runner logic for when a real GitHub Actions workflow is doing
the actual test execution (see .github/workflows/karate-ci.yml).

In that setup, Runner's job is NOT to run Maven itself -- GitHub Actions'
`pull_request` trigger already did that automatically the moment Publisher
opened the PR. Runner's real job is to read the result back via the
Checks API and hand a clean status to Reporter.

This is deliberately a separate module from runner.py (which runs Maven
locally for the no-GitHub POC path) so you can see both patterns side by
side and swap based on whether GITHUB_* env vars are configured -- same
pattern as publisher.py's graceful skip.
"""
import time, requests
API_ROOT = "https://api.github.com"

def _headers(token): return {"Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

def get_pr_head_sha(owner, repo, pr_number, token):
    resp = requests.get(f"{API_ROOT}/repos/{owner}/{repo}/pulls/{pr_number}", headers=_headers(token))
    resp.raise_for_status()
    return resp.json()["head"]["sha"]

def wait_for_checks(owner, repo, sha, token, timeout_s=600, poll_s=15):
    url = f"{API_ROOT}/repos/{owner}/{repo}/commits/{sha}/check-runs"
    elapsed = 0
    while elapsed < timeout_s:
        resp = requests.get(url, headers=_headers(token))
        resp.raise_for_status()
        runs = resp.json().get("check_runs", [])
        if runs and all(r["status"] == "completed" for r in runs):
            conclusions = [r["conclusion"] for r in runs]
            overall = "passed" if all(c == "success" for c in conclusions) else "failed"
            return {"status": overall, "checks": [{"name": r["name"], "conclusion": r["conclusion"]} for r in runs]}
        time.sleep(poll_s); elapsed += poll_s
    return {"status": "timeout", "reason": f"Checks did not complete within {timeout_s}s"}

def trigger_manual_run(owner, repo, workflow_file, ref, tags, token):
    url = f"{API_ROOT}/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"
    resp = requests.post(url, headers=_headers(token), json={"ref": ref, "inputs": {"tags": tags}})
    resp.raise_for_status()