#!/usr/bin/env python3
"""Public-only issue manifest. No private repositories, secrets or report bodies."""
import json
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

SOURCES = {
    "energy": "https://docs.agim.ca/intel/",
    "optical": "https://docs.energizeos.com/intel/",
}
ISSUE = re.compile(r"^20[0-9]{2}-w(?:0[1-9]|[1-4][0-9]|5[0-3])$")
DATE = re.compile(r"^20[0-9]{2}-[0-9]{2}-[0-9]{2}$")

class IssueLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.issues = set()
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href", "")
        match = re.search(r"(?:^|/)(20[0-9]{2}-w[0-9]{2})/?(?:#.*)?$", href)
        if match and ISSUE.fullmatch(match.group(1)):
            self.issues.add(match.group(1))

def fetch(url):
    with urlopen(Request(url, headers={"User-Agent": "Corporate-Public-Intelligence-Manifest/1.0"}), timeout=20) as response:
        if response.status != 200 or response.geturl().split("?")[0] != url:
            raise ValueError("Source response or redirect not allowed")
        return response.read(500000).decode("utf-8")

def build(kind):
    root = SOURCES[kind]
    parser = IssueLinks()
    parser.feed(fetch(root))
    issues = []
    for issue in sorted(parser.issues, reverse=True)[:30]:
        try:
            metadata = json.loads(fetch(root + issue + "/meta.json"))
            published = metadata.get("published_on") or metadata.get("date")
            if not isinstance(published, str) or not DATE.fullmatch(published):
                continue
            published_day = date.fromisoformat(published)
            if published_day > date.today() or published_day.isocalendar()[:2] != (int(issue[:4]), int(issue[-2:])):
                continue
            issues.append({"issue": issue, "published": published, "url": root + issue + "/"})
        except (OSError, ValueError, KeyError, TypeError):
            continue
    if not issues:
        raise ValueError("No verified public issue metadata; refusing update")
    return {"schema_version": 1, "source": root, "issues": issues}

if __name__ == "__main__":
    kind = sys.argv[1]
    target = Path(sys.argv[2])
    manifest = build(kind)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("VERIFIED_PUBLIC_ISSUES", kind, len(manifest["issues"]), manifest["issues"][0]["issue"])
