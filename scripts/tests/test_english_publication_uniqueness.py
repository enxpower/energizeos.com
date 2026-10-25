"""Fail closed on repeated weekly editorial claims and duplicate primary URLs."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("english_editions", ROOT / "scripts/english_editions.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

class PublicationUniqueness(unittest.TestCase):
    def test_existing_editorial_history_is_distinct(self):
        self.assertGreaterEqual(len(engine.load_issues(ROOT)), 2)

    def test_exact_repeated_headline_blocked(self):
        issues = copy.deepcopy(engine.load_issues(ROOT))
        issues[1]["headline"] = issues[0]["headline"]
        with self.assertRaisesRegex(ValueError, "Repeated headline"):
            engine._reject_repeated_editorial(issues)

    def test_near_identical_development_facts_blocked(self):
        issues = copy.deepcopy(engine.load_issues(ROOT))
        issues[1]["developments"][0]["fact"] = issues[0]["developments"][0]["fact"] + "!"
        with self.assertRaisesRegex(ValueError, "(Near-duplicate|Repeated) development"):
            engine._reject_repeated_editorial(issues)

    def test_duplicate_source_url_in_one_issue_blocked(self):
        config = json.loads((ROOT / "content/intelligence/config.json").read_text())
        issue = copy.deepcopy(engine.load_issues(ROOT)[0])
        issue["sources"][1]["url"] = issue["sources"][0]["url"]
        issue["approval"]["content_sha256"] = engine.digest(issue)
        with self.assertRaisesRegex(ValueError, "Duplicate primary-source URL"):
            engine.validate_issue(issue, config)

    def test_unrelated_current_editions_remain_publishable(self):
        engine._reject_repeated_editorial(engine.load_issues(ROOT))

if __name__ == "__main__":
    unittest.main()
