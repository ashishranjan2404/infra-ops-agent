"""Generate a REAL episode-log JSONL grounded in actual CIDG scenario YAMLs.

For each scenario that defines trap_actions + canonical_fix, we emit two episodes:
a "safe" agent that applies the canonical fix, and a "trappy" agent that pulls the
scenario's trap action. failed_checks is computed with the SAME predicate
rex/scoring.py uses (action_is_trap, mirrored in trap_avoidance.py), so the metric
has authoritative, non-fabricated trap labels to aggregate.

    python3 make_rollouts.py > rollouts.jsonl
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trap_avoidance import action_is_trap, load_trap_specs  # noqa: E402

SCEN_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "scenarios", "cidg", "generated"))


def _load_full(path):
    try:
        import yaml
        with open(path) as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return None


def main():
    out = []
    if not os.path.isdir(SCEN_DIR):
        print(f"# scenarios dir missing: {SCEN_DIR}", file=sys.stderr)
        return 1
    for fn in sorted(os.listdir(SCEN_DIR)):
        if not fn.endswith((".yaml", ".yml")):
            continue
        doc = _load_full(os.path.join(SCEN_DIR, fn))
        if not doc:
            continue
        traps = doc.get("trap_actions") or []
        fix_steps = (doc.get("canonical_fix") or {}).get("steps") or []
        if not traps or not fix_steps:
            continue
        sid = (doc.get("meta") or {}).get("id") or os.path.splitext(fn)[0]

        # safe agent: apply canonical fix
        safe_actions = [{"tool": s["tool"], "args": s.get("args", {})} for s in fix_steps]
        out.append(_episode(sid, safe_actions, traps))

        # trappy agent: pull the trap action
        t0 = traps[0]
        trap_actions = [{"tool": t0["tool"], "args": {"target": (t0.get("args") or {}).get("target")
                                                      or t0.get("target")}}]
        out.append(_episode(sid, trap_actions, traps))

    for ep in out:
        print(json.dumps(ep))
    print(f"# wrote {len(out)} episodes from {SCEN_DIR}", file=sys.stderr)
    return 0


def _episode(sid, actions, traps):
    hit = any(action_is_trap(a, traps) for a in actions)
    fc = ["trap_action"] if hit else []
    return {"scenario": sid, "actions": actions, "trap_actions": traps,
            "failed_checks": fc, "resolved": not hit}


if __name__ == "__main__":
    raise SystemExit(main())
