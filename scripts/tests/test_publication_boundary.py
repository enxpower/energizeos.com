"""Guard the actual public HTML against the confirmed production regressions."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from public_copy_gate import check_markup

class PublicationBoundary(unittest.TestCase):
    def test_unresolved_templates_are_rejected(self):
        for body in ('<p>${publicWeeklyIssues("energy")}</p>', '<p>%%DATA_CARDS%%</p>', '<meta content="{{headline}}">'):
            self.assertTrue(check_markup(body, "fixture"), body)

    def test_encoded_and_raw_chinese_research_links_are_rejected(self):
        for host in ('docs.agim.ca', 'docs.energizeos.com'):
            for path in ('/intel/', '/%69ntel/2026-w43/'):
                body = '<a href="https://' + host + path + '">Read</a>'
                self.assertTrue(check_markup(body, "fixture"), body)

    def test_english_primary_source_and_local_article_are_allowed(self):
        self.assertFalse(check_markup('<p>Grid procurement</p><a href="/insights/intelligence/2026-w43/">Read</a><a href="https://www.eia.gov/">Source</a>', "fixture"))

if __name__ == '__main__':
    unittest.main()
