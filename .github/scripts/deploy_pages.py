#!/usr/bin/env python3
"""Publish the Pages artifact and wait for GitHub to finish.

actions/deploy-pages clamps its timeout input to 600000 ms, then cancels the
deployment. A custom-domain publish can stay in updating_pages past that cap,
so cancelling aborts a deploy that is still going out. This waits 30 minutes
and does not cancel an in-progress deployment.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

WAIT_SECONDS = 30 * 60
MAX_ATTEMPTS = 3
RETRY_PAUSE_SECONDS = 30
MAX_STATUS_ERRORS = 10

FINAL_FAILURES = {
    "deployment_failed": "Deployment failed, try again later.",
    "deployment_content_failed": (
        "Artifact could not be deployed. Check for symlinks, hard links, or a site over 10GB."
    ),
    "deployment_cancelled": "Deployment cancelled.",
    "deployment_lost": "Deployment failed to report final status.",
}
RETRYABLE = {"deployment_failed", "deployment_lost"}


def classify(status):
    if status == "succeed":
        return "succeed"
    if status in FINAL_FAILURES:
        return "fail"
    return "in_progress"


def _request(method, url, token, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code} {detail}") from exc


def _oidc_token():
    url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    request_token = os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"bearer {request_token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode())
    value = payload.get("value")
    if not value:
        raise RuntimeError("GitHub did not return an OIDC token for the Pages deployment.")
    return value


def _api_base():
    return os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")


def _deployment_url(deployment_id):
    repo = os.environ["GITHUB_REPOSITORY"]
    return f"{_api_base()}/repos/{repo}/pages/deployments/{deployment_id}"


def _write_page_url(page_url):
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path or not page_url:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"page_url={page_url}\n")


def create_deployment(build_version):
    artifact_id = os.environ["ARTIFACT_ID"].strip()
    if not artifact_id:
        raise RuntimeError("Missing ARTIFACT_ID from the Pages upload step.")
    repo = os.environ["GITHUB_REPOSITORY"]
    url = f"{_api_base()}/repos/{repo}/pages/deployments"
    print(f"Creating Pages deployment for {build_version} from artifact {artifact_id}", flush=True)
    # Do not print the request body. It contains the OIDC token.
    payload = _request(
        "POST",
        url,
        os.environ["GITHUB_TOKEN"],
        {
            "artifact_id": int(artifact_id),
            "pages_build_version": build_version,
            "oidc_token": _oidc_token(),
        },
    )
    status_url = payload.get("status_url") or ""
    deployment_id = payload.get("id") or status_url.rstrip("/").split("/")[-1] or build_version
    page_url = payload.get("page_url") or ""
    print(f"Created deployment {deployment_id}", flush=True)
    if page_url:
        print(f"Page URL: {page_url}", flush=True)
        _write_page_url(page_url)
    return str(deployment_id)


def poll_deployment(deployment_id, deadline):
    interval = 5
    errors = 0
    token = os.environ["GITHUB_TOKEN"]
    url = _deployment_url(deployment_id)
    while True:
        if time.time() >= deadline:
            print(
                "Pages is still publishing after 30 minutes. Leaving this deployment running.",
                flush=True,
            )
            return "timeout"
        try:
            payload = _request("GET", url, token)
        except RuntimeError as exc:
            errors += 1
            print(f"Status check failed ({errors}/{MAX_STATUS_ERRORS}): {exc}", flush=True)
            if errors >= MAX_STATUS_ERRORS:
                raise
            time.sleep(min(interval, max(0, deadline - time.time())))
            continue

        errors = 0
        status = payload.get("status") or ""
        kind = classify(status)
        if kind == "succeed":
            print("Reported success!", flush=True)
            return "succeed"
        if kind == "fail":
            print(f"Current status: {status}", flush=True)
            print(FINAL_FAILURES[status], flush=True)
            return status
        print(f"Current status: {status or '(empty)'}", flush=True)
        remaining = deadline - time.time()
        time.sleep(min(interval, max(0, remaining)))
        interval = min(interval * 1.5, 30)


def deploy():
    missing = [
        name
        for name in (
            "ARTIFACT_ID",
            "GITHUB_TOKEN",
            "GITHUB_REPOSITORY",
            "GITHUB_SHA",
            "ACTIONS_ID_TOKEN_REQUEST_URL",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        )
        if not os.environ.get(name)
    ]
    if missing:
        raise SystemExit("Missing environment: " + ", ".join(missing))
    sha = os.environ["GITHUB_SHA"]
    deadline = time.time() + WAIT_SECONDS
    for attempt in range(1, MAX_ATTEMPTS + 1):
        build_version = sha if attempt == 1 else f"{sha}-retry{attempt}"
        deployment_id = create_deployment(build_version)
        result = poll_deployment(deployment_id, deadline)
        if result == "succeed":
            return
        if result == "timeout":
            raise SystemExit(1)
        if result not in RETRYABLE or attempt == MAX_ATTEMPTS or time.time() >= deadline:
            raise SystemExit(1)
        print(f"Attempt {attempt} ended with {result}. Retrying without cancelling it.", flush=True)
        time.sleep(min(RETRY_PAUSE_SECONDS, max(0, deadline - time.time())))
    raise SystemExit(1)


def _check():
    expected = {
        "succeed": "succeed",
        "deployment_failed": "fail",
        "deployment_content_failed": "fail",
        "deployment_cancelled": "fail",
        "deployment_lost": "fail",
        "deployment_queued": "in_progress",
        "updating_pages": "in_progress",
        "syncing_files": "in_progress",
        "deployment_attempt_error": "in_progress",
        "": "in_progress",
    }
    for status, kind in expected.items():
        got = classify(status)
        if got != kind:
            raise SystemExit(f"classify({status!r}) returned {got}, expected {kind}")
    print("deploy_pages checks passed")


def main(argv):
    if argv[1:] == ["--check"]:
        _check()
        return
    if argv[1:]:
        raise SystemExit(f"Unknown arguments: {' '.join(argv[1:])}")
    deploy()


if __name__ == "__main__":
    main(sys.argv)
