#!/usr/bin/env python3
"""Fail closed on unreachable primary-source links when adding public Intelligence issues.

Only NEW issue routes are checked against the immutable Git baseline. Unchanged
historical articles are not rewritten or held hostage by a temporary source outage.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ISSUES = "content/intelligence/issues/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_probe(url, allowed_hosts, *, opener=urlopen):
    address = urlsplit(url)
    require(address.scheme == "https" and address.hostname in allowed_hosts and not address.username
            and not address.password and not address.fragment, "Unapproved primary-source address: " + url)
    req = Request(url, headers={
        "User-Agent": "English-Intelligence-Editorial-Link-Verification/1.0",
        "Accept": "text/html,application/xhtml+xml,application/pdf,text/plain",
    })
    with opener(req, timeout=18) as response:
        final_url = response.geturl()
        target = urlsplit(final_url)
        require(target.scheme == "https" and target.hostname in allowed_hosts
                and not target.username and not target.password,
                "Primary-source redirect left the approved official hosts: " + url)
        require(response.status == 200, "Primary-source HTTP failure: " + url)
        mime = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
        require(mime in {"text/html", "application/xhtml+xml", "application/pdf", "text/plain"},
                "Unexpected primary-source content type: " + url + " " + mime)
        sample = response.read(131073)
        require(len(sample) >= 60, "Empty or truncated primary-source response: " + url)
        if mime == "application/pdf":
            require(sample.startswith(b"%PDF-"), "Invalid source PDF response: " + url)
        elif mime in {"text/html", "application/xhtml+xml"}:
            markup = sample.decode("utf-8", errors="replace")
            title = re.search(r"<title\b[^>]*>(.*?)</title>", markup, flags=re.I | re.S)
            if title:
                cleaned = re.sub(r"<[^>]+>", " ", title.group(1))
                cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
                require(not any(bad in cleaned for bad in (
                    "404", "page not found", "access denied", "just a moment",
                    "attention required", "sign in", "login required")),
                    "Primary-source webpage is an error or login screen: " + url)
            require("<html" in markup.lower() or "<!doctype html" in markup.lower(),
                    "Primary-source HTML body is malformed: " + url)
    return final_url


def new_issues(root, baseline):
    saved = subprocess.run(["git", "show", baseline + ":content/intelligence/manifest.json"],
                           cwd=root, text=True, capture_output=True)
    require(saved.returncode == 0, "Publication baseline manifest unavailable: " + baseline)
    former = json.loads(saved.stdout)
    current = json.loads((root / "content/intelligence/manifest.json").read_text(encoding="utf-8"))
    require(former["schema_version"] == 1 and current["schema_version"] == 1
            and former["language"] == current["language"] == "en", "Unrecognized edition manifests")
    old_slugs = former["issues"]
    current_slugs = current["issues"]
    require(len(old_slugs) == len(set(old_slugs)) and len(current_slugs) == len(set(current_slugs)),
            "Duplicate edition slug")
    require(current_slugs[:len(old_slugs)] == old_slugs, "Edited or reordered published history")
    return [json.loads((root / ISSUES / (slug + ".json")).read_text(encoding="utf-8"))
            for slug in current_slugs[len(old_slugs):]]


def verify_new(root, baseline, *, probe=source_probe):
    config = json.loads((root / "content/intelligence/config.json").read_text(encoding="utf-8"))
    allowed = set(config["allowed_source_hosts"])
    additions = new_issues(root, baseline)
    checked_urls = set()
    for issue in additions:
        require(issue.get("approval", {}).get("status") == "approved",
                "Unapproved edition cannot enter live link preflight")
        require(issue.get("language") == "en" and issue.get("sources"),
                "Complete English cited issue required")
        for source in issue["sources"]:
            url = source["url"]
            require(source.get("kind") == "primary", "Only primary sources are allowed")
            if url in checked_urls:
                continue
            try:
                destination = probe(url, allowed)
            except Exception as exc:
                raise ValueError("LIVE_PRIMARY_SOURCE=FAIL " + issue["issue"] + " " + url
                                 + " (" + str(exc) + ")") from exc
            print("LIVE_PRIMARY_SOURCE=PASS issue=" + issue["issue"] + " url=" + url
                  + " resolved=" + destination)
            checked_urls.add(url)
    print("NEW_ENGLISH_SOURCE_LINKS=PASS issues=" + str(len(additions))
          + " verified_urls=" + str(len(checked_urls)))
    return len(additions), len(checked_urls)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    args = parser.parse_args()
    verify_new(ROOT, args.baseline)


if __name__ == "__main__":
    main()
