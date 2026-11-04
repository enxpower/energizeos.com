"""Verify deterministic data refresh, revisions and atomic failure behavior."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import refresh_optical_metrics as metrics


class OpticalMetrics(unittest.TestCase):
    def test_public_dataset_rejects_private_fields_and_invalid_numbers(self):
        rows = [metrics.parse_csv(series, ('observation_date,' + series + '\n2026-09-01,100\n').encode()) for series in metrics.SERIES]
        for key, value in [('recommended_action', 'Private lead'), ('value', float('nan')), ('source_url', 'https://unverified.example/')]:
            modified = [dict(row) for row in rows]
            modified[0][key] = value
            with self.assertRaises(ValueError):
                metrics.validate_dataset({'schema_version': 1, 'metrics': modified})

    def test_latest_nonmissing_observation_and_revision(self):
        body = b'observation_date,IPN33592S\n2026-08-01,71.2410\n2026-09-01,73.3782\n2026-10-01,.\n'
        row = metrics.parse_csv('IPN33592S', body)
        self.assertEqual((row['period'], row['value']), ('2026-09-01', 73.3782))
        self.assertEqual(len(row['source_sha256']), 64)

    def test_wrong_series_duplicate_future_and_nonfinite_rejected(self):
        for body in [b'observation_date,WRONG\n2026-09-01,10\n',
                     b'observation_date,IPN33592S\n2026-09-01,10\n2026-09-01,12\n',
                     b'observation_date,IPN33592S\n2099-01-01,10\n',
                     b'observation_date,IPN33592S\n2026-09-01,nan\n']:
            with self.assertRaises(ValueError):
                metrics.parse_csv('IPN33592S', body)

    def test_one_failed_source_preserves_all_published_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root / 'insights/intelligence/data.json'
            page = root / 'insights/intelligence/index.html'
            data.parent.mkdir(parents=True)
            data.write_text('previous data')
            page.write_text('previous page')
            def unavailable(series):
                raise OSError('source unavailable')
            with self.assertRaises(OSError):
                metrics.refresh(root, fetch=unavailable)
            self.assertEqual(data.read_text(), 'previous data')
            self.assertEqual(page.read_text(), 'previous page')

    def test_unchanged_data_is_noop_and_period_rollback_is_rejected(self):
        root = Path(__file__).resolve().parents[2]
        source = (root / 'insights/intelligence/index.html').read_text()
        with tempfile.TemporaryDirectory() as folder:
            work = Path(folder)
            page = work / 'insights/intelligence/index.html'
            page.parent.mkdir(parents=True)
            page.write_text(source)
            def fixture(series):
                return ('observation_date,' + series + '\n2026-09-01,100.25\n').encode()
            self.assertTrue(metrics.refresh(work, fetch=fixture))
            before = page.read_bytes()
            self.assertFalse(metrics.refresh(work, fetch=fixture))
            self.assertEqual(page.read_bytes(), before)
            def old(series):
                return ('observation_date,' + series + '\n2026-08-01,99\n').encode()
            with self.assertRaises(ValueError):
                metrics.refresh(work, fetch=old)
            self.assertEqual(page.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
