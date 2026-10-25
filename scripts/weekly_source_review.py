#!/usr/bin/env python3
"""Stage English primary-source candidates for editorial review; never publish."""
import argparse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FEEDS = {
    "energy": (
        ("U.S. Department of Energy News", "https://www.energy.gov/rss/energygov/2193718"),
        ("U.S. EIA Today in Energy", "https://www.eia.gov/rss/todayinenergy.xml"),
    ),
    "optical": (
        ("CRTC Daily Releases", "https://crtc.gc.ca/eng/rss/daily.xml"),
        ("CRTC Broadband Fund", "https://crtc.gc.ca/eng/rss/bbf.atom.xml"),
    ),
}
TOPICS = {
    "energy": ("battery", "storage", "grid", "electricity", "electric", "transmission",
               "power", "interconnection", "substation", "transformer", "reliability",
               "capacity", "bess", "data center"),
    "optical": ("fiber", "fibre", "optical", "broadband", "telecom", "network",
                "internet", "connectivity", "wireless", "infrastructure",
                "dwdm", "coherent", "transport"),
}
CJK = re.compile(r"[\u3400-\u9fff]")

def text(node, name):
    for child in node:
        if child.tag.split("}")[-1] == name and child.text:
            return child.text.strip()
    return ""

def parse_date(value):
    if not value:
        return None
    try:
        found = parsedate_to_datetime(value)
    except (ValueError, TypeError, IndexError):
        try:
            found = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if found.tzinfo is None:
        return None
    return found.astimezone(timezone.utc)

def parse_feed(data, *, now, source_name, allowed_hosts, kind):
    root = ET.fromstring(data)
    if root.tag.split("}")[-1] not in ("rss", "feed", "RDF"):
        raise ValueError("Unexpected feed format")
    entries = [n for n in root.iter() if n.tag.split("}")[-1] in ("item", "entry")]
    if not entries:
        raise ValueError("Primary feed has no entries")
    seen, candidates = set(), []
    for item in entries[:120]:
        title = text(item, "title")
        link = text(item, "link")
        if not link:
            for child in item:
                if child.tag.split("}")[-1] == "link" and child.attrib.get("rel", "alternate") == "alternate":
                    link = child.attrib.get("href", "")
                    break
        published = parse_date(text(item, "pubDate") or text(item, "published") or text(item, "updated") or text(item, "date"))
        if not title or CJK.search(title) or not published or published > now + timedelta(hours=2) or published < now - timedelta(days=21):
            continue
        address = urlsplit(link)
        if address.scheme != "https" or address.hostname not in allowed_hosts or address.username or address.password or address.fragment:
            continue
        if link in seen or not any(keyword in title.lower() for keyword in TOPICS[kind]):
            continue
        seen.add(link)
        candidates.append({
            "source": source_name,
            "title": title[:230],
            "url": link,
            "source_published_at": published.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "source_verified": False,
            "editorial_approval": "required",
        })
    return candidates

def download(url):
    req = Request(url, headers={
        "User-Agent": "Corporate-Intelligence-Source-Review/1.0",
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
    })
    with urlopen(req, timeout=18) as response:
        if response.status != 200:
            raise ValueError("HTTP " + str(response.status))
        resolved = urlsplit(response.geturl())
        if resolved.scheme != "https" or resolved.hostname != urlsplit(url).hostname:
            raise ValueError("Feed redirected outside official source host")
        data = response.read(512001)
    if len(data) > 512000:
        raise ValueError("Oversized official feed")
    return data

def collect(kind, allowed_hosts, *, now, fetch=download):
    rows, errors, passed = [], [], []
    for name, url in FEEDS[kind]:
        try:
            items = parse_feed(fetch(url), now=now, source_name=name,
                               allowed_hosts=allowed_hosts, kind=kind)
            rows.extend(items)
            passed.append({"name": name, "feed": url, "candidate_count": len(items)})
        except Exception as error:
            errors.append({"name": name, "feed": url,
                           "error": type(error).__name__ + ": " + str(error)[:220]})
    unique = {row["url"]: row for row in rows}
    candidates = sorted(unique.values(), key=lambda row: (
        row["source_published_at"], row["title"]), reverse=True)[:30]
    status = "blocked" if errors else ("review_required" if candidates else "no_new_evidence")
    return {
        "schema_version": 1,
        "kind": kind,
        "collected_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "status": status, "feeds_ok": passed, "feed_errors": errors,
        "candidates": candidates, "published_article": False,
        "reviewed_manifest_changed": False,
        "policy": "Candidates are unverified; independent source and English editorial approval are required before publication.",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / "content/intelligence/config.json").read_text(encoding="utf-8"))
    kind = config["kind"]
    if kind not in FEEDS:
        raise ValueError("Unsupported publication kind")
    manifest = ROOT / "content/intelligence/manifest.json"
    previous = sha256(manifest.read_bytes()).hexdigest()
    result = collect(kind, set(config["allowed_source_hosts"]), now=datetime.now(timezone.utc))
    result["reviewed_manifest_sha256"] = previous
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert sha256(manifest.read_bytes()).hexdigest() == previous, "Manifest modified by review-only pipeline"
    print("ENGLISH_WEEKLY_SOURCE_REVIEW=" + result["status"].upper(),
          "candidates=" + str(len(result["candidates"])),
          "feeds=" + str(len(result["feeds_ok"])),
          "errors=" + str(len(result["feed_errors"])))
    for issue in result["feed_errors"]:
        print("FEED_ERROR", issue["name"], issue["error"], file=sys.stderr)
    if result["feed_errors"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
