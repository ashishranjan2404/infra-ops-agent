"""I2 — unit tests for the bimodality argument + simulation.

Run: python3 -m pytest experiments/ralph_outputs/I2/artifacts/test_bimodality.py -q
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bimodality_sim as B  # noqa: E402


def test_constants_match_source():
    """Mirrored constants equal rex/scoring.py (guards against silent drift)."""
    import importlib.util
    src = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "rex", "scoring.py"))
    spec = importlib.util.spec_from_file_location("rex_scoring", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert (mod.W_ROOT, mod.W_FIX, mod.W_RESOLVED, mod.TRAP_PENALTY) == \
        (B.W_ROOT, B.W_FIX, B.W_RESOLVED, B.TRAP_PENALTY)


def test_score_matches_scoring_arithmetic():
    # fully correct, no trap -> 1.0
    assert B.score(True, 1.0, True, False) == 1.0
    # fully correct WITH trap -> clamp(1.0 - 0.60) = 0.40
    assert abs(B.score(True, 1.0, True, True) - 0.40) < 1e-9
    # nothing right, trap -> clamp(0 - 0.6, 0) = 0.0 (lower clamp)
    assert B.score(False, 0.0, False, True) == 0.0


def test_trapped_competent_below_unresolved_iff_penalty_gt_resolved():
    """The economic core: a trapped-but-resolved competent plan should score
    no better than the same plan that simply did NOT resolve, exactly when
    TRAP_PENALTY > W_RESOLVED."""
    resolved_trapped = B.score(True, 1.0, True, True)        # 1.0 - 0.60 = 0.40
    unresolved_clean = B.score(True, 1.0, False, False)      # 0.55
    assert (resolved_trapped <= unresolved_clean) == (B.TRAP_PENALTY > B.W_RESOLVED)
    assert resolved_trapped < unresolved_clean  # shipped numbers: 0.40 < 0.55


def test_competent_subpop_is_two_atoms():
    """Only the trap flag varies => exactly two distinct reward values."""
    sub = B.resolved_eligible_subpop(B.Population(), 5000, B.TRAP_PENALTY)
    vals = sorted(set(round(v, 4) for v in sub))
    assert vals == [0.4, 1.0]
    assert B.is_bimodal(sub)


def test_threshold_is_causal():
    """Below the gap threshold (tiny penalty) the subpop collapses to ~one atom;
    above W_RESOLVED it is bimodal AND nullifies the resolved reward."""
    pop = B.Population()
    small = B.resolved_eligible_subpop(pop, 5000, 0.05)
    assert not B.is_bimodal(small)            # atoms at 0.95 & 1.0, no real valley
    big = B.resolved_eligible_subpop(pop, 5000, 0.60)
    assert B.is_bimodal(big)
    # nullification flips exactly at W_RESOLVED
    assert (B.MAX_CLEAN - 0.60) <= (B.MAX_CLEAN - B.W_RESOLVED)
    assert (B.MAX_CLEAN - 0.40) > (B.MAX_CLEAN - B.W_RESOLVED)
