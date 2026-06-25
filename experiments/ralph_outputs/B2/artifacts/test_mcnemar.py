#!/usr/bin/env python3
"""Self-contained unit tests for mcnemar.py (stdlib unittest, no pytest needed)."""
import importlib.util
import math
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mcnemar", os.path.join(_HERE, "mcnemar.py"))
mc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mc)


class TestBinary(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(mc.to_binary(0.8, 0.8), 1)   # >= passes
        self.assertEqual(mc.to_binary(0.79, 0.8), 0)
        self.assertEqual(mc.to_binary(1.0, 0.8), 1)
        self.assertEqual(mc.to_binary(0.0, 0.8), 0)


class TestMcNemarTable(unittest.TestCase):
    def test_known_discordant(self):
        # A passes the 3 where B fails; B passes the 1 where A fails.
        a = [1, 1, 1, 0, 1, 1]
        b = [0, 0, 0, 1, 1, 1]
        t = mc.mcnemar_table(a, b)
        self.assertEqual(t["a_pass_b_fail"], 3)
        self.assertEqual(t["a_fail_b_pass"], 1)
        self.assertEqual(t["n_discordant"], 4)
        self.assertEqual(t["both_pass"], 2)
        self.assertEqual(t["both_fail"], 0)

    def test_no_discordant_gives_p1(self):
        a = [1, 1, 0, 0]
        b = [1, 1, 0, 0]
        t = mc.mcnemar_table(a, b)
        self.assertEqual(t["n_discordant"], 0)
        self.assertEqual(t["p_exact"], 1.0)
        self.assertEqual(t["chi2_cc"], 0.0)

    def test_exact_binomial_matches_hand_calc(self):
        # b01=9, b10=1 -> two-sided exact = 2 * P(X<=1 | Bin(10,.5))
        a = [1] * 9 + [0] + [1] * 5   # 9 A-only passes, 1 B-only pass, 5 both
        b = [0] * 9 + [1] + [1] * 5
        t = mc.mcnemar_table(a, b)
        self.assertEqual(t["a_pass_b_fail"], 9)
        self.assertEqual(t["a_fail_b_pass"], 1)
        expected = min(1.0, 2 * (math.comb(10, 0) + math.comb(10, 1)) * 0.5 ** 10)
        self.assertAlmostEqual(t["p_exact"], round(expected, 6), places=6)

    def test_symmetry_swaps_cells(self):
        a = [1, 1, 1, 0]
        b = [0, 0, 0, 1]
        ta = mc.mcnemar_table(a, b)
        tb = mc.mcnemar_table(b, a)
        self.assertEqual(ta["a_pass_b_fail"], tb["a_fail_b_pass"])
        self.assertEqual(ta["p_exact"], tb["p_exact"])  # p is direction-agnostic

    def test_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            mc.mcnemar_table([1, 0], [1])


class TestHolm(unittest.TestCase):
    def test_holm_monotone_and_correction(self):
        pairs = [("p1", 0.001), ("p2", 0.04), ("p3", 0.6)]
        out = mc.holm_bonferroni(pairs, alpha=0.05)
        # p1: 3*0.001=0.003 sig; p2: 2*0.04=0.08 NOT sig at 0.05; p3 follows
        self.assertTrue(out["p1"]["significant_holm"])
        self.assertFalse(out["p2"]["significant_holm"])
        self.assertFalse(out["p3"]["significant_holm"])
        # monotonicity: p_holm non-decreasing in p_raw order
        self.assertLessEqual(out["p1"]["p_holm"], out["p2"]["p_holm"])
        self.assertLessEqual(out["p2"]["p_holm"], out["p3"]["p_holm"])

    def test_all_significant(self):
        pairs = [("a", 0.0), ("b", 0.0001)]
        out = mc.holm_bonferroni(pairs, alpha=0.05)
        self.assertTrue(out["a"]["significant_holm"])
        self.assertTrue(out["b"]["significant_holm"])


class TestAlignedBits(unittest.TestCase):
    def test_alignment_order(self):
        data = {
            "threshold": 0.8,
            "by_condition": {
                "x": {"per_incident_rewards": {"inc1": [1.0, 0.0], "inc2": [0.5, 0.9]}},
            },
        }
        bits = mc.aligned_bits(data, "x", ["inc1", "inc2"], 0.8)
        self.assertEqual(bits, [1, 0, 0, 1])

    def test_missing_incident_raises(self):
        data = {"by_condition": {"x": {"per_incident_rewards": {"inc1": [1.0]}}}}
        with self.assertRaises(KeyError):
            mc.aligned_bits(data, "x", ["inc1", "missing"], 0.8)


class TestEndToEnd(unittest.TestCase):
    def test_analyze_synthetic_file(self):
        # 2 conditions, 2 incidents, 2 seeds. cond A strictly dominates B.
        data = {
            "model": "synthetic", "threshold": 0.8, "seeds": 2,
            "incidents_by_family": {"simple": ["i1"], "novel": ["i2"]},
            "by_condition": {
                "A": {"per_incident_rewards": {"i1": [1.0, 1.0], "i2": [1.0, 1.0]}},
                "B": {"per_incident_rewards": {"i1": [0.0, 0.0], "i2": [0.0, 1.0]}},
            },
        }
        rep = mc.analyze_file(data, threshold_override=None, alpha=0.05)
        self.assertIn("overall", rep["by_family"])
        ov = rep["by_family"]["overall"]["pairs"]["A__vs__B"]
        self.assertEqual(ov["a_pass_b_fail"], 3)  # A passes 3 where B fails
        self.assertEqual(ov["a_fail_b_pass"], 0)
        self.assertEqual(rep["n_condition_pairs"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
