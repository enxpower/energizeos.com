"""Exercise publication admission and immutable history, not display-string snapshots."""
import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

class EditionAdmission(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]

    def test_reviewed_manifest_has_real_complete_local_editions(self):
        import english_editions as pub
        issues = pub.load_issues(self.root)
        self.assertGreaterEqual(len(issues), 2)
        self.assertGreater(len({x['headline'] for x in issues}), 1)
        self.assertEqual(issues, sorted(issues, key=lambda x:x['published_at'], reverse=True))

    def test_tampered_or_future_issue_cannot_be_admitted(self):
        import english_editions as pub
        config = json.loads((self.root/'content/intelligence/config.json').read_text())
        valid = pub.load_issues(self.root)[0]
        for field, value in [('headline', 'Silently replaced history'), ('published_at', '2099-01-01T00:00:00Z'), ('language', 'zh'), ('developments', []), ('published_at', '2026-10-25T23:30:00+14:00')]:
            bad = copy.deepcopy(valid);bad[field] = value
            with self.assertRaises(ValueError, msg=field):pub.validate_issue(bad, config)

    def test_missing_primary_evidence_or_review_is_rejected(self):
        import english_editions as pub
        config = json.loads((self.root/'content/intelligence/config.json').read_text())
        valid = pub.load_issues(self.root)[0]
        for key in ('sources', 'approval', 'watchlist', 'uncertainties'):
            bad=copy.deepcopy(valid);bad.pop(key)
            with self.assertRaises(ValueError, msg=key):pub.validate_issue(bad, config)

    def test_new_article_must_be_tracked_for_static_pages(self):
        import english_editions as pub
        import tempfile
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            subprocess.run(['git','init','-q',folder],check=True)
            page=root/'insights/intelligence/2026-w43/index.html'
            page.parent.mkdir(parents=True);page.write_text('English article')
            with self.assertRaises(ValueError):pub.check_tracked_output(root)
            subprocess.run(['git','add','insights'],cwd=root,check=True)
            pub.check_tracked_output(root)

    def test_unlisted_public_edition_route_is_rejected(self):
        import english_editions as pub
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            rogue=root/'insights/intelligence/2025-w42/index.html'
            rogue.parent.mkdir(parents=True);rogue.write_text('Unreviewed edition')
            with self.assertRaises(ValueError):pub.check_route_inventory(root, pub.load_issues(self.root))

    def test_source_unavailability_cannot_change_published_history(self):
        import english_editions as pub
        issues=pub.load_issues(self.root)
        with self.assertRaises(ValueError):pub.check_history(issues[1:], issues)
        bad=copy.deepcopy(issues);bad[0]['headline']='Replacement'
        with self.assertRaises(ValueError):pub.check_history(bad, issues)
        pub.check_history(issues, issues)

if __name__ == '__main__': unittest.main()
