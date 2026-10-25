#!/usr/bin/env python3
"""Prepare an evidence-only editorial intake packet. Never generate or publish an article."""
import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CJK = re.compile(r"[\u3400-\u9fff]")
STEPS = [
    "Open and read the original primary source; verify its full article and source date.",
    "Cross-check every proposed factual claim, number, status and geographic scope.",
    "Write independent English engineering and commercial implications with uncertainties.",
    "Check relevant product/legal/trade claims and avoid private or unsupported information.",
    "Obtain an explicit editorial review, approval identity and reviewed content digest.",
    "Submit the approved source JSON and append-only manifest through the existing PR, CI and live publication gates.",
]

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def utc(value):
    require(isinstance(value, str) and value.endswith("Z"), "UTC timestamp required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Malformed timestamp") from exc
    require(parsed.tzinfo is not None, "Missing timezone")
    return parsed.astimezone(timezone.utc)

def make_packet(review, *, kind, allowed_hosts, cited_urls, manifest_sha, now):
    require(review.get("schema_version") == 1 and review.get("kind") == kind, "Incorrect source review identity")
    require(review.get("reviewed_manifest_sha256") == manifest_sha, "Stale publication baseline")
    require(review.get("published_article") is False and review.get("reviewed_manifest_changed") is False,
            "Source review attempted to change publication")
    require(review.get("status") in ("blocked", "review_required", "no_new_evidence"),
            "Unknown source-qualification status")
    require(isinstance(review.get("candidates"), list), "Missing source candidate list")
    collected = utc(review.get("collected_at"))
    require(abs((now - collected).total_seconds()) <= 3 * 86400, "Stale or future collection")
    proposed_week = collected.isocalendar()
    accepted = []
    for candidate in review["candidates"]:
        require(candidate.get("source_verified") is False
                and candidate.get("editorial_approval") == "required",
                "Source review must not self-approve")
        title, url = candidate.get("title"), candidate.get("url")
        require(isinstance(title, str) and title.strip() and not CJK.search(title), "Invalid English title")
        require(isinstance(url, str), "Missing source URL")
        parsed = urlsplit(url)
        require(parsed.scheme == "https" and parsed.hostname in allowed_hosts
                and not parsed.username and not parsed.password and not parsed.fragment,
                "Source outside publisher allowlist")
        date = utc(candidate.get("source_published_at"))
        require(collected - timedelta(days=21) <= date <= collected + timedelta(hours=2),
                "Unqualified source date")
        if url in cited_urls or any(x["primary_url"] == url for x in accepted):
            continue
        accepted.append({
            "source": candidate["source"], "headline_for_review": title,
            "primary_url": url, "source_published_at": candidate["source_published_at"],
            "fact_verified": False, "full_source_read": False, "proposed_claims": [],
            "editorial_approval": "required",
        })
    require(not review.get("feed_errors") or review["status"] == "blocked",
            "Fetch errors must block publication")
    status = "blocked" if review["status"] == "blocked" else (
        "editorial_review_required" if accepted else "no_new_evidence")
    return {
        "schema_version": 1, "kind": kind, "working_week": f"{proposed_week.year}-W{proposed_week.week:02d}",
        "source_collection_at": review["collected_at"], "source_manifest_sha256": manifest_sha,
        "status": status, "draft_only": True, "publication_permitted": False,
        "site_or_manifest_changed": False,
        "source_feed_errors": review.get("feed_errors", []),
        "uncited_candidates": accepted if status != "blocked" else [],
        "editorial_checklist": STEPS,
        "note": "This packet is not an article, source verification, approval or publication instruction.",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / "content/intelligence/config.json").read_text(encoding="utf-8"))
    manifest_path = ROOT / "content/intelligence/manifest.json"
    baseline = sha256(manifest_path.read_bytes()).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cited = set()
    for slug in manifest["issues"]:
        issue = json.loads((ROOT / "content/intelligence/issues" / (slug + ".json")).read_text(encoding="utf-8"))
        cited.update(source["url"] for source in issue["sources"])
    review = json.loads(args.input.read_text(encoding="utf-8"))
    packet = make_packet(review, kind=config["kind"], allowed_hosts=set(config["allowed_source_hosts"]),
                         cited_urls=cited, manifest_sha=baseline, now=datetime.now(timezone.utc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    require(sha256(manifest_path.read_bytes()).hexdigest() == baseline, "Publication baseline modified")
    print("ENGLISH_EDITORIAL_INTAKE=" + packet["status"].upper(),
          "uncited_candidates=" + str(len(packet["uncited_candidates"])),
          "publication_permitted=false")

if __name__ == "__main__":
    main()
