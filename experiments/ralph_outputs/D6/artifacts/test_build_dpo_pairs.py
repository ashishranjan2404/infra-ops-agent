"""Unit tests for the DPO pair constructor (stdlib unittest, no third-party deps)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from build_dpo_pairs import construct_pairs, DPOExample, build_prompt  # noqa: E402

SPECS = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "opensre-traj", "specs")


def _row(scn, model, reward, answer="ans", incident=None):
    return {
        "scenario_id": scn,
        "incident": incident or scn.split("-", 1)[-1],
        "model": model,
        "reward": reward,
        "answer": answer,
    }


class TestConstructPairs(unittest.TestCase):
    def test_chosen_has_higher_reward(self):
        rows = [_row("s1", "m1", 0.8, "good"), _row("s1", "m2", 0.2, "bad")]
        pairs = construct_pairs(rows, min_margin=0.1, specs_dir=SPECS)
        self.assertEqual(len(pairs), 1)
        p = pairs[0]
        self.assertGreater(p.chosen_reward, p.rejected_reward)
        self.assertEqual(p.chosen, "good")
        self.assertEqual(p.rejected, "bad")
        self.assertAlmostEqual(p.margin, 0.6)

    def test_orientation_independent_of_input_order(self):
        # lower-reward row first must still produce chosen=higher
        rows = [_row("s1", "m2", 0.2, "bad"), _row("s1", "m1", 0.8, "good")]
        p = construct_pairs(rows, min_margin=0.1, specs_dir=SPECS)[0]
        self.assertEqual(p.chosen, "good")

    def test_min_margin_filters(self):
        rows = [_row("s1", "m1", 0.55, "a"), _row("s1", "m2", 0.50, "b")]
        self.assertEqual(construct_pairs(rows, min_margin=0.1, specs_dir=SPECS), [])
        self.assertEqual(len(construct_pairs(rows, min_margin=0.01, specs_dir=SPECS)), 1)

    def test_empty_answers_skipped(self):
        rows = [_row("s1", "m1", 0.8, ""), _row("s1", "m2", 0.2, "bad")]
        self.assertEqual(construct_pairs(rows, min_margin=0.1, specs_dir=SPECS), [])

    def test_identical_text_skipped(self):
        rows = [_row("s1", "m1", 0.8, "same"), _row("s1", "m2", 0.2, "same")]
        self.assertEqual(construct_pairs(rows, min_margin=0.1, specs_dir=SPECS), [])

    def test_no_cross_scenario_pairs(self):
        rows = [_row("s1", "m1", 0.9, "a"), _row("s2", "m2", 0.1, "b")]
        # one row each scenario -> no intra-scenario pair possible
        self.assertEqual(construct_pairs(rows, min_margin=0.1, specs_dir=SPECS), [])

    def test_max_per_scenario_cap(self):
        rows = [_row("s1", f"m{i}", 0.1 * i, f"a{i}") for i in range(1, 6)]
        pairs = construct_pairs(rows, min_margin=0.05, max_pairs_per_scenario=2, specs_dir=SPECS)
        self.assertEqual(len(pairs), 2)
        # capped pairs are the highest-margin ones, sorted descending
        self.assertGreaterEqual(pairs[0].margin, pairs[1].margin)

    def test_deterministic(self):
        rows = [_row("s1", "m1", 0.8, "a"), _row("s1", "m2", 0.2, "b"),
                _row("s2", "m3", 0.9, "c"), _row("s2", "m4", 0.3, "d")]
        self.assertEqual(construct_pairs(rows, specs_dir=SPECS),
                         construct_pairs(rows, specs_dir=SPECS))

    def test_returns_dpoexample_with_prompt(self):
        rows = [_row("s1", "m1", 0.8, "good"), _row("s1", "m2", 0.2, "bad")]
        p = construct_pairs(rows, min_margin=0.1, specs_dir=SPECS)[0]
        self.assertIsInstance(p, DPOExample)
        self.assertTrue(p.prompt)

    def test_build_prompt_fallback_for_missing_spec(self):
        out = build_prompt("does_not_exist_xyz", specs_dir=SPECS)
        self.assertIn("does_not_exist_xyz", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
