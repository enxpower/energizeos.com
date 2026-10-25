"""Strict editorial staging tests: packets never self-publish or invent factual claims."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "prepare_editorial_packet.py"
spec = importlib.util.spec_from_file_location("prepare_editorial_packet", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NOW = datetime(2026,10,25,16,0,tzinfo=timezone.utc)
BASE = {
    "schema_version":1, "kind":"optical", "collected_at":"2026-10-25T15:00:00Z",
    "reviewed_manifest_sha256":"digest", "status":"review_required",
    "feed_errors":[], "published_article":False, "reviewed_manifest_changed":False,
    "candidates":[{
        "source":"CRTC","title":"Broadband connection technology consultation",
        "url":"https://crtc.gc.ca/eng/example",
        "source_published_at":"2026-10-24T12:00:00Z",
        "source_verified":False, "editorial_approval":"required",
    }]
}

def stage(record, cited=()):
    return m.make_packet(record, kind="optical", allowed_hosts={"crtc.gc.ca"},
                         cited_urls=set(cited), manifest_sha="digest", now=NOW)

class EditorialIntakeTests(unittest.TestCase):
    def test_stage_is_unverified_and_unpublished(self):
        result=stage(BASE)
        self.assertEqual(result["status"],"editorial_review_required")
        self.assertEqual(len(result["uncited_candidates"]),1)
        self.assertFalse(result["publication_permitted"])
        self.assertFalse(result["uncited_candidates"][0]["fact_verified"])
        self.assertEqual(result["uncited_candidates"][0]["proposed_claims"],[])

    def test_cited_source_not_recycled(self):
        result=stage(BASE,cited=("https://crtc.gc.ca/eng/example",))
        self.assertEqual(result["status"],"no_new_evidence")
        self.assertFalse(result["publication_permitted"])

    def test_bad_source_is_rejected(self):
        q=dict(BASE,candidates=[dict(BASE["candidates"][0],url="https://evil.invalid/")])
        with self.assertRaises(ValueError):stage(q)

    def test_self_approval_is_rejected(self):
        q=dict(BASE,candidates=[dict(BASE["candidates"][0],source_verified=True)])
        with self.assertRaises(ValueError):stage(q)

    def test_stale_manifest_is_rejected(self):
        with self.assertRaises(ValueError):stage(dict(BASE,reviewed_manifest_sha256="stale"))

    def test_blocked_feed_withholds_draft(self):
        q=dict(BASE,status="blocked",feed_errors=[{"error":"HTTP 403"}])
        result=stage(q)
        self.assertEqual(result["status"],"blocked")
        self.assertEqual(result["uncited_candidates"],[])

    def test_no_evidence_is_safe(self):
        result=stage(dict(BASE,status="no_new_evidence",candidates=[]))
        self.assertEqual(result["status"],"no_new_evidence")
        self.assertFalse(result["publication_permitted"])
