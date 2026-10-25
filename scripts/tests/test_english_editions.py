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
        for field, value in [('headline', 'Silently replaced history'), ('published_at', '2099-01-01T00:00:00Z'), ('language', 'zh'), ('developments', [])]:
            bad = copy.deepcopy(valid);bad[field] = value
            with self.assertRaises(ValueError, msg=field):pub.validate_issue(bad, config)

    def test_missing_primary_evidence_or_review_is_rejected(self):
        import english_editions as pub
        config = json.loads((self.root/'content/intelligence/config.json').read_text())
        valid = pub.load_issues(self.root)[0]
        for key in ('sources', 'approval', 'watchlist', 'uncertainties'):
            bad=copy.deepcopy(valid);bad.pop(key)
            with self.assertRaises(ValueError, msg=key):pub.validate_issue(bad, config)

    def test_source_unavailability_cannot_change_published_history(self):
        import english_editions as pub
        issues=pub.load_issues(self.root)
        with self.assertRaises(ValueError):pub.check_history(issues[1:], issues)
        bad=copy.deepcopy(issues);bad[0]['headline']='Replacement'
        with self.assertRaises(ValueError):pub.check_history(bad, issues)
        pub.check_history(issues, issues)

if __name__ == '__main__': unittest.main()
