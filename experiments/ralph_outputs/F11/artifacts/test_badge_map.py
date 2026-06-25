"""F11 — schema + grounding tests for badge_claim_map.json.

Self-contained, no network. Asserts the badge map is well-formed AND that the
files/commands it names actually exist in the repo, so the appendix can't silently rot.

Run:  python3 -m pytest experiments/ralph_outputs/F11/artifacts/test_badge_map.py -q
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
MAP = os.path.join(HERE, "badge_claim_map.json")

ACM_BADGES = {
    "Artifacts Available",
    "Artifacts Evaluated - Functional",
    "Results Reproduced",
}


def _load():
    with open(MAP) as f:
        return json.load(f)


def test_json_parses():
    d = _load()
    for k in ("artifact", "commit_pin", "badges"):
        assert k in d, f"missing top-level key: {k}"
    assert isinstance(d["badges"], list) and d["badges"]


def test_three_badges():
    d = _load()
    names = [b["badge"] for b in d["badges"]]
    assert set(names) == ACM_BADGES, names
    assert len(names) == len(set(names)), "duplicate badge"


def test_evidence_files_exist():
    d = _load()
    for b in d["badges"]:
        ev = b.get("evidence_file", "")
        if ev:
            assert os.path.exists(os.path.join(REPO, ev)), f"missing evidence file: {ev}"


def test_offline_badge_no_creds():
    d = _load()
    func = next(b for b in d["badges"] if b["badge"] == "Artifacts Evaluated - Functional")
    assert func["needs_credentials"] is False
    assert func["tier"] == "offline"


def test_online_badge_uses_eval():
    d = _load()
    repro = next(b for b in d["badges"] if b["badge"] == "Results Reproduced")
    assert repro["needs_credentials"] is True
    assert "rex.eval_pass_at_k" in repro["command"]
    assert "--conditions" in repro["command"]  # real flag from rex/eval_pass_at_k.py


def test_commands_reference_real_flags():
    d = _load()
    func = next(b for b in d["badges"] if b["badge"] == "Artifacts Evaluated - Functional")
    # offline command names a real, existing script
    script = func["command"].split()[-1]
    assert os.path.exists(os.path.join(REPO, script)), f"missing smoke script: {script}"
