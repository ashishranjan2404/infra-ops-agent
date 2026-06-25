"""D13: pin the reward-hacking findings as regression tests.

These tests DOCUMENT exploits against rex.scoring.deterministic_judge. They assert
the *current* (vulnerable) behavior so that if the judge is later hardened, these
tests FLIP and signal that the vulnerability is closed. They do not modify core.

Run: python3 -m pytest experiments/ralph_outputs/D13/artifacts/test_reward_hack_probe.py -q
"""
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from rex import scoring  # noqa: E402
from rex.harness import load_scenario  # noqa: E402

scoring.JUDGE_MODE = "deterministic"
OOM = load_scenario("oom_kill")
GCP = load_scenario("gcp_service_control")


def dj(stated, sc):
    return scoring.judge_diagnosis(stated, sc)


# ---- EXPLOITS the judge currently FALLS FOR (vulnerable) --------------------
def test_negated_gold_still_credited():
    # Bag-of-words ignores "NOT": denying the mechanism still scores CORRECT.
    assert dj(f"this is definitely NOT {OOM.gold_root_description}", OOM) is True


def test_single_gold_token_credited():
    # One discriminative noun, zero mechanism stated -> still CORRECT.
    assert dj("the issue is related to leak somehow, unclear", OOM) is True


def test_wrong_component_right_mechanism_credited():
    # Right mechanism words bolted to the wrong component -> CORRECT (no component check).
    g = scoring._stems(OOM.gold_root_description)
    h = set().union(*[scoring._stems(x) for x in OOM.red_herring_hints])
    mech = " ".join(sorted(g - h))
    assert dj(f"the load-balancer exhibits {mech}", OOM) is True


def test_homoglyph_evades_herring_penalty():
    # Cyrillic homoglyphs on the herrings dodge the penalty; gold (ASCII) still scores.
    table = {"a": "а", "e": "е", "o": "о"}
    base = OOM.gold_root_description + " not " + " ".join(OOM.red_herring_hints)
    obf = "".join(table.get(c, c) for c in base)
    assert dj(obf, OOM) is True


# ---- guards the judge correctly RESISTS (must stay robust) ------------------
def test_whitespace_rejected():
    assert dj("   \n\t .,;:!? ---  ", OOM) is False


def test_pure_herring_rejected():
    assert dj("the service simply needs more replicas", OOM) is False
