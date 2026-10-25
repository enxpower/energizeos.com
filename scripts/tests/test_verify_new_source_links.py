"""Negative coverage for primary-source publication gates, with no live network in tests."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("live_new_source", ROOT / "scripts/verify_new_source_links.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Response:
    status = 200
    headers = {"Content-Type": "text/html; charset=utf-8"}
    def __init__(self, url="https://www.eia.gov/article", title="Electric Power Monthly"):
        self.url, self.title = url, title
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def geturl(self): return self.url
    def read(self, n):
        return (("<!doctype html><html><head><title>" + self.title +
                 "</title></head><body><p>Original official publication</p></body></html>").encode())

class PrimaryLinkVerification(unittest.TestCase):
    def test_official_live_html(self):
        result = m.source_probe("https://www.eia.gov/article", {"www.eia.gov"},
                                opener=lambda req, timeout: Response())
        self.assertEqual(result, "https://www.eia.gov/article")

    def test_offsite_redirect_fails(self):
        with self.assertRaisesRegex(ValueError, "redirect left"):
            m.source_probe("https://www.eia.gov/article", {"www.eia.gov"},
                           opener=lambda req, timeout: Response("https://evil.invalid/article"))

    def test_soft_404_and_challenge_pages_fail(self):
        for title in ("404 Not Found", "Access Denied", "Just a Moment..."):
            with self.subTest(title=title):
                with self.assertRaisesRegex(ValueError, "error or login"):
                    m.source_probe("https://www.eia.gov/article", {"www.eia.gov"},
                                   opener=lambda req, timeout: Response(title=title))

    def test_fake_host_and_http_fail(self):
        for url in ("http://www.eia.gov/article", "https://evil.invalid/article"):
            with self.assertRaisesRegex(ValueError, "Unapproved"):
                m.source_probe(url, {"www.eia.gov"}, opener=lambda req, timeout: Response())

    def test_baseline_with_no_new_issues_is_network_free(self):
        count = m.verify_new(ROOT, "HEAD", probe=lambda *args: self.fail("Unexpected network request"))
        self.assertEqual(count, (0, 0))

    def test_new_issue_with_unavailable_link_stops_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "content/intelligence/issues").mkdir(parents=True)
            (root / "content/intelligence/config.json").write_text(
                json.dumps({"allowed_source_hosts":["www.eia.gov"]}))
            (root / "content/intelligence/manifest.json").write_text(
                json.dumps({"schema_version":1,"language":"en","issues":["2026-w43","2026-w44"]}))
            issue = {"issue":"2026-w44","language":"en","approval":{"status":"approved"},
                     "sources":[{"kind":"primary","url":"https://www.eia.gov/not-available"}]}
            (root / "content/intelligence/issues/2026-w44.json").write_text(json.dumps(issue))
            with patch.object(m, "new_issues", return_value=[issue]):
                with self.assertRaisesRegex(ValueError, "LIVE_PRIMARY_SOURCE=FAIL"):
                    m.verify_new(root, "origin/main",
                                 probe=lambda *args: (_ for _ in ()).throw(OSError("HTTP 404")))

if __name__ == "__main__":
    unittest.main()
