"""Independently reconcile the published worksheet's DC and AC energy boundaries."""
import csv
from decimal import Decimal as D
from pathlib import Path
import unittest

class DispatchReference(unittest.TestCase):
    def test_energy_and_power_fail_for_different_reasons(self):
        root = Path(__file__).resolve().parents[2]
        with (root / 'downloads/battery-dispatch-reserve.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual([r['case'] for r in rows], ['A', 'B', 'C'])
        expected = [('0.09', True, True), ('-0.575', False, True), ('0.77', True, False)]
        for row, (headroom, energy_pass, power_pass) in zip(rows, expected):
            # Independent energy conservation: DC withdrawal must supply the load
            # and AC auxiliaries after one-way conversion, without spending reserve.
            dc_above_floor = D(row['available_dc_mwh']) * (D(row['start_soc_fraction']) - D(row['reserve_soc_fraction']))
            ac_required = (D(row['load_ac_mw']) + D(row['aux_ac_mw'])) * D(row['hours'])
            dc_required = ac_required / D(row['discharge_efficiency'])
            actual_headroom = (dc_above_floor - dc_required) * D(row['discharge_efficiency'])
            self.assertAlmostEqual(actual_headroom, D(headroom), places=12)
            self.assertEqual(D(row['energy_headroom_mwh']), D(headroom))
            self.assertEqual(dc_required <= dc_above_floor, energy_pass)
            self.assertEqual(D(row['pcs_required_ac_mw']) <= D(row['pcs_ceiling_ac_mw']), power_pass)
            self.assertEqual(row['energy_pass'], str(energy_pass))
            self.assertEqual(row['power_pass'], str(power_pass))
