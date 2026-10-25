#!/usr/bin/env python3
"""Verify deployed, independent English Intelligence against its live issue manifest."""
import json
import re
import sys
import time
import urllib.request
from urllib.parse import urlsplit

domain = sys.argv[1]
assert domain in {"agim.ca", "energizeos.com"}, "Unapproved domain"
origin = "https://" + domain
base = "/insights/intelligence/"
cjk = re.compile(r"[\u3400-\u9fff]")
unresolved = re.compile(r"\$\{|%%[A-Z_]+%%|\{\{")


def fetch(route):
    assert route.startswith("/") and not route.startswith("//")
    url = origin + route
    error = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "English-Intelligence-Live-Acceptance/1.0"})
            with urllib.request.urlopen(req, timeout=25) as response:
                assert response.status == 200, f"HTTP {response.status}: {url}"
                assert response.geturl().rstrip("/") == url.rstrip("/"), f"Redirected: {url}"
                return response.read(950_000).decode("utf-8", errors="strict")
        except Exception as exc:
            error = exc
            if attempt < 3:
                time.sleep(8)
    raise AssertionError(f"Public route unavailable: {url}: {error}")


manifest = json.loads(fetch(base + "issues.json"))
assert manifest.get("schema_version") == 1 and manifest.get("language") == "en"
issues = manifest.get("issues")
assert isinstance(issues, list) and len(issues) >= 2
assert len({item["issue"] for item in issues}) == len(issues)
assert issues == sorted(issues, key=lambda item: item["published_at"], reverse=True)
routes = ["/insights/", base, base + "archive/"]
for item in issues:
    route = item["url"]
    assert re.fullmatch(r"/insights/intelligence/20[0-9]{2}-(?:w[0-9]{2}|reference-[0-9]{2})/", route)
    routes.append(route)

for route in routes:
    body = fetch(route)
    assert '<html lang="en">' in body, f"Non-English declaration: {route}"
    assert f'href="{origin + route}"' in body, f"Canonical mismatch: {route}"
    assert not cjk.search(body) and not unresolved.search(body), f"Content/template leakage: {route}"
    assert "docs.agim.ca/intel/" not in body and "docs.energizeos.com/" not in body, f"Isolated publisher link: {route}"
    if route in ("/insights/", base):
        for marker in ("Latest Intelligence", "Previous Edition", "Browse All Editions"):
            assert marker in body, f"Missing reader navigation: {marker} {route}"
    if route == base + "archive/":
        for item in issues:
            assert item["url"] in body, f"Missing archived edition: {item['issue']}"
    for item in issues:
        if route == item["url"]:
            assert item["headline"].replace("&", "&amp;") in body or item["headline"] in body, f"Article identity: {route}"
            assert item["published_at"] in body, f"Publication date: {route}"
            assert body.count('id="source-') >= 3, f"Primary source references missing: {route}"
            assert "Executive briefing" in body and "What remains uncertain" in body, f"Not a complete article: {route}"
    print("LIVE_ENGLISH_ROUTE=PASS", origin + route)
print(f"LIVE_ENGLISH_PUBLICATION=PASS domain={domain} issues={len(issues)} routes={len(routes)}")
