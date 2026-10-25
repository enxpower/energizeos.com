"""Qualification tests: bad feeds, stale evidence and missing review always fail closed."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import unittest

script = Path(__file__).resolve().parents[1] / "weekly_source_review.py"
spec = importlib.util.spec_from_file_location("weekly_source_review", script)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NOW = datetime(2026, 10, 25, 14, 30, tzinfo=timezone.utc)
RSS = b'''<rss version="2.0"><channel>
<item><title>Battery storage grid investment announced</title><link>https://www.energy.gov/articles/example</link><pubDate>Sat, 24 Oct 2026 12:00:00 GMT</pubDate></item>
<item><title>Grid malicious host</title><link>https://evil.invalid/grids</link><pubDate>Sat, 24 Oct 2026 12:00:00 GMT</pubDate></item>
<item><title>Battery from future</title><link>https://www.energy.gov/articles/future</link><pubDate>Sat, 12 Dec 2026 12:00:00 GMT</pubDate></item>
<item><title>Unrelated entertainment</title><link>https://www.energy.gov/articles/unrelated</link><pubDate>Sat, 24 Oct 2026 12:00:00 GMT</pubDate></item>
<item><title>Battery without date</title><link>https://www.energy.gov/articles/undated</link></item>
</channel></rss>'''
ATOM = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
<title>New broadband infrastructure decision</title>
<link href="https://crtc.gc.ca/eng/example" rel="alternate"/>
<updated>2026-10-24T12:00:00Z</updated></entry></feed>'''

class SourceReviewTests(unittest.TestCase):
    def test_rss_trust_filter(self):
        rows = m.parse_feed(RSS, now=NOW, source_name="DOE", allowed_hosts={"www.energy.gov"}, kind="energy")
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["source_verified"])
        self.assertEqual(rows[0]["editorial_approval"], "required")

    def test_atom_source(self):
        rows = m.parse_feed(ATOM, now=NOW, source_name="CRTC", allowed_hosts={"crtc.gc.ca"}, kind="optical")
        self.assertEqual(len(rows), 1)

    def test_unavailable_feed_fail_closed(self):
        result = m.collect("energy", {"www.energy.gov"}, now=NOW, fetch=lambda _: b"<html/>")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(len(result["feed_errors"]), 2)
        self.assertFalse(result["published_article"])

    def test_partial_failure_fail_closed(self):
        def request(url):
            if "eia.gov" in url:
                raise TimeoutError("unavailable")
            return RSS
        result = m.collect("energy", {"www.energy.gov"}, now=NOW, fetch=request)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(len(result["candidates"]), 1)
        self.assertFalse(result["reviewed_manifest_changed"])

    def test_no_fresh_evidence_preserves_history(self):
        old = RSS.replace(b"24 Oct 2026", b"24 Jan 2026")
        result = m.collect("energy", {"www.energy.gov"}, now=NOW, fetch=lambda _: old)
        self.assertEqual(result["status"], "no_new_evidence")
        self.assertFalse(result["published_article"])
