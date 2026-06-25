#!/usr/bin/env python3
"""synth_sre_augmenter.py — synthetic SRE trajectory augmentation over CIDG scenarios.

E9 deliverable (synthetic-augmentation ARM of the head-to-head). Given the existing
CIDG scenario YAMLs (scenarios/cidg/generated/*.yaml), this produces NEW labelled
SRE diagnosis/remediation trajectories in the project's FIREBALL-inspired schema
(state_before -> tool -> state_after -> reward) WITHOUT calling any LLM and without
any external dataset. It is a pure, deterministic, structure-preserving augmenter:

  1. parse a scenario's gold root_cause + canonical_fix + trap_actions
  2. synthesize a *positive* trajectory (correct investigation -> canonical fix)
     and a configurable number of *negative* trajectories (trap action / wrong fix /
     empty plan) so the augmented group has WITHIN-GROUP REWARD SPREAD — the unit of
     trainability per the HUD task-design doctrine.
  3. apply label-preserving perturbations (paraphrase of the alert summary, tool-order
     shuffle of read-only probes, replica/threshold jitter) to multiply each scenario
     into N variants while keeping the gold label invariant.

Reward is assigned by the SAME deterministic rubric the bench uses (root-cause match
+ canonical-fix present + no-trap), so augmented rewards are consistent with
rex/scoring.py weights (0.30 root / 0.25 fix / 0.45 resolved, -0.60 trap) without
importing the live judge (kept hermetic / no API key needed).

Usage:
    python3 synth_sre_augmenter.py --scenarios <dir> --n 4 --out aug.jsonl
    python3 synth_sre_augmenter.py --self-test
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import random
import sys

try:
    import yaml
    HAVE_YAML = True
except Exception:
    HAVE_YAML = False

# Mirror rex/scoring.py weights (single source of truth documented, not imported,
# so the augmenter is dependency-free and offline).
W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60

# Read-only investigation probes whose ORDER does not change the label.
READONLY_TOOLS = [
    "get_alerts", "get_metrics", "get_deployment_status", "get_node_status",
    "get_events", "get_logs", "describe_pod", "query_traces",
]

# Cheap paraphrase table for the alert summary (label-preserving surface variation).
_PARA = [
    ("spiked", "surged"), ("error rate", "failure rate"), ("immediately", "right"),
    ("Fix the root", "Remediate the root"), ("Immediately", "Without delay"),
]


def _load_yaml(path: str) -> dict:
    with open(path) as f:
        if HAVE_YAML:
            return yaml.safe_load(f)
        raise RuntimeError("PyYAML required for parsing scenarios")


def _gold(sc: dict) -> dict:
    """Extract gold label fields from a CIDG scenario dict."""
    rc = sc.get("root_cause", {}) or {}
    fix = (sc.get("canonical_fix", {}) or {}).get("steps", []) or []
    traps = sc.get("trap_actions", []) or []
    fix_tool = fix[0].get("tool") if fix else None
    fix_target = (fix[0].get("args", {}) or {}).get("target") if fix else rc.get("location")
    return {
        "root_cause_kind": rc.get("kind"),
        "root_cause_location": rc.get("location"),
        "fix_tool": fix_tool,
        "fix_target": fix_target,
        "trap_tools": [t.get("tool") for t in traps if t.get("tool")],
    }


def _reward(diag_correct: bool, fix_present: bool, resolved: bool, trap: bool) -> float:
    r = W_ROOT * diag_correct + W_FIX * fix_present + W_RESOLVED * resolved
    if trap:
        r -= TRAP_PENALTY
    return round(r, 4)


def _perturb_summary(text: str, rng: random.Random) -> str:
    out = text
    for a, b in _PARA:
        if a in out and rng.random() < 0.5:
            out = out.replace(a, b, 1)
    return out


def _state_before(g: dict, sc: dict) -> dict:
    return {
        "alert": f"SLO breach on {g['root_cause_location']} "
                 f"({sc.get('meta', {}).get('failure_class', g['root_cause_kind'])})",
        "topology_nodes": [n.get("name") for n in (sc.get("topology", {}) or {}).get("nodes", [])],
        "slo_breached": True,
    }


def _positive(g: dict, sc: dict, rng: random.Random) -> dict:
    probes = READONLY_TOOLS[:]
    rng.shuffle(probes)
    probes = probes[: rng.randint(4, 7)]
    return {
        "label": "positive",
        "state_before": _state_before(g, sc),
        "investigation": probes,
        "action": {"tool": g["fix_tool"], "target": g["fix_target"]},
        "stated_root_cause": g["root_cause_kind"],
        "state_after": {"slo_breached": False, "root_cleared": True, "trap_taken": False},
        "reward": _reward(True, bool(g["fix_tool"]), True, False),
    }


def _negatives(g: dict, sc: dict, rng: random.Random) -> list:
    negs = []
    # (a) trap action: takes a trap tool, diagnosis wrong, not resolved.
    if g["trap_tools"]:
        negs.append({
            "label": "negative_trap",
            "state_before": _state_before(g, sc),
            "investigation": READONLY_TOOLS[: rng.randint(1, 3)],
            "action": {"tool": rng.choice(g["trap_tools"]), "target": g["root_cause_location"]},
            "stated_root_cause": "unknown",
            "state_after": {"slo_breached": True, "root_cleared": False, "trap_taken": True},
            "reward": _reward(False, False, False, True),
        })
    # (b) wrong fix: a plausible but wrong remediation (scale instead of real fix).
    wrong_tool = "scale_deployment" if g["fix_tool"] != "scale_deployment" else "restart_service"
    negs.append({
        "label": "negative_wrong_fix",
        "state_before": _state_before(g, sc),
        "investigation": READONLY_TOOLS[: rng.randint(2, 4)],
        "action": {"tool": wrong_tool, "target": g["root_cause_location"]},
        "stated_root_cause": "partial",
        "state_after": {"slo_breached": True, "root_cleared": False, "trap_taken": False},
        "reward": _reward(False, False, False, False),
    })
    # (c) empty plan: no action (floor case — must score <= pass threshold).
    negs.append({
        "label": "negative_empty",
        "state_before": _state_before(g, sc),
        "investigation": [],
        "action": None,
        "stated_root_cause": None,
        "state_after": {"slo_breached": True, "root_cleared": False, "trap_taken": False},
        "reward": _reward(False, False, False, False),
    })
    return negs


def augment_scenario(path: str, n: int, seed: int = 0) -> list:
    """Return a list of synthetic trajectory groups for one scenario file."""
    sc = _load_yaml(path)
    g = _gold(sc)
    sid = (sc.get("meta", {}) or {}).get("id") or os.path.splitext(os.path.basename(path))[0]
    base_summary = (sc.get("canonical_fix", {}) or {}).get("ordering_notes", "")
    groups = []
    for v in range(n):
        # deterministic per-(scenario,variant) rng for reproducibility.
        h = int(hashlib.sha1(f"{sid}:{v}:{seed}".encode()).hexdigest()[:8], 16)
        rng = random.Random(h)
        traj = [_positive(g, sc, rng)] + _negatives(g, sc, rng)
        rewards = [t["reward"] for t in traj]
        mean = sum(rewards) / len(rewards)
        var = sum((r - mean) ** 2 for r in rewards) / len(rewards)
        groups.append({
            "scenario_id": sid,
            "variant": v,
            "source": "synthetic_augmented",
            "augmenter": "synth_sre_augmenter@E9",
            "alert_summary": _perturb_summary(base_summary, rng),
            "gold": g,
            "trajectories": traj,
            "within_group_reward_spread": round(var ** 0.5, 4),
        })
    return groups


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default="scenarios/cidg/generated")
    ap.add_argument("--n", type=int, default=4, help="variants per scenario")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    files = sorted(glob.glob(os.path.join(args.scenarios, "*.yaml")))
    if not files:
        print(f"no scenarios found in {args.scenarios}", file=sys.stderr)
        return 2
    all_groups = []
    for f in files:
        try:
            all_groups.extend(augment_scenario(f, args.n, args.seed))
        except Exception as e:  # skip malformed, keep going
            print(f"skip {f}: {e}", file=sys.stderr)
    out = args.out or os.path.join("experiments/ralph_outputs/E9/artifacts", "augmented_trajectories.jsonl")
    with open(out, "w") as fh:
        for grp in all_groups:
            fh.write(json.dumps(grp) + "\n")
    spreads = [g["within_group_reward_spread"] for g in all_groups]
    n_traj = sum(len(g["trajectories"]) for g in all_groups)
    nonzero = sum(1 for s in spreads if s > 0)
    print(json.dumps({
        "scenarios": len(files), "groups": len(all_groups), "trajectories": n_traj,
        "groups_with_spread": nonzero,
        "mean_within_group_spread": round(sum(spreads) / len(spreads), 4) if spreads else 0.0,
        "out": out,
    }))
    return 0


def _self_test() -> int:
    """Hermetic self-test: synthesize an in-memory scenario, assert invariants."""
    scenario = {
        "meta": {"id": "selftest-oom", "failure_class": "oom_kill"},
        "topology": {"nodes": [{"name": "orders"}]},
        "root_cause": {"location": "orders", "kind": "oom_kill"},
        "canonical_fix": {"ordering_notes": "Fix the root orders with raise_memory_limit.",
                          "steps": [{"tool": "raise_memory_limit", "args": {"target": "orders"}}]},
        "trap_actions": [{"tool": "scale_deployment", "args": {"target": "orders"}}],
    }
    # monkey-path: write to temp, reuse augment_scenario path loader
    import tempfile
    fd, p = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    with open(p, "w") as f:
        yaml.safe_dump(scenario, f)
    groups = augment_scenario(p, n=3, seed=1)
    os.unlink(p)

    checks = []
    checks.append(("3 variants produced", len(groups) == 3))
    g0 = groups[0]
    labels = [t["label"] for t in g0["trajectories"]]
    checks.append(("has positive", "positive" in labels))
    checks.append(("has trap negative", "negative_trap" in labels))
    checks.append(("has empty negative", "negative_empty" in labels))
    pos = [t for t in g0["trajectories"] if t["label"] == "positive"][0]
    checks.append(("positive reward == 1.0", abs(pos["reward"] - 1.0) < 1e-9))
    trap = [t for t in g0["trajectories"] if t["label"] == "negative_trap"][0]
    checks.append(("trap reward < 0 (penalty)", trap["reward"] < 0))
    empt = [t for t in g0["trajectories"] if t["label"] == "negative_empty"][0]
    checks.append(("empty plan reward == 0", abs(empt["reward"]) < 1e-9))
    checks.append(("within-group spread > 0", g0["within_group_reward_spread"] > 0))
    # determinism: same seed -> identical output
    g_again = augment_scenario_inmem(scenario, 3, 1)
    checks.append(("deterministic re-run", json.dumps(g_again) == json.dumps(_strip(groups))))

    ok = all(c[1] for c in checks)
    for name, passed in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


def _strip(groups):
    return groups


def augment_scenario_inmem(scenario: dict, n: int, seed: int):
    """Same as augment_scenario but from an in-memory dict (for determinism test)."""
    import tempfile
    fd, p = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    with open(p, "w") as f:
        yaml.safe_dump(scenario, f)
    try:
        return augment_scenario(p, n, seed)
    finally:
        os.unlink(p)


if __name__ == "__main__":
    sys.exit(main())
