"""C4 validator: re-apply the 3 synthesized rules (harness_synth_v2.json) through the
REAL trusted interpreter (rex.harness_synth.is_safe_synth) on the HELD-OUT incidents and
reproduce the published confusion + worked examples.

This is an ANALYSIS artifact for task C4. It imports rex.harness_synth read-only and never
calls main() (which would rewrite a core JSON). Run:

    cd /Users/mei/rl && python3 experiments/ralph_outputs/C4/artifacts/validate_rules.py
"""
from __future__ import annotations

import json
import os
import sys

REPO = "/Users/mei/rl"
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from rex.harness_synth import (  # noqa: E402
    FEATURES, confusion, is_safe_synth, labeled_examples,
)
from rex.harness_synth import handwritten_pred  # noqa: E402

V2_JSON = os.path.join(REPO, "rex", "runs", "harness_synth_v2.json")
HELDOUT = ["cpu_saturation_leaf", "singleton_node_notready", "azure_ddos"]


def load_rules() -> list:
    d = json.load(open(V2_JSON))
    return d["rules"], d


def heldout_examples() -> list:
    return [e for n in HELDOUT for e in labeled_examples(n)]


def active(feats: dict) -> dict:
    return {k: v for k, v in feats.items() if k in FEATURES and v is True}


def main() -> int:
    rules, d = load_rules()
    ex = heldout_examples()
    c = confusion(rules, ex)
    pub = d["heldout_table"]["synthesized (v2)"]

    print("=" * 74)
    print("C4 — re-applying the 3 synthesized rules to HELD-OUT via is_safe_synth")
    print("=" * 74)
    print(f"n_rules = {len(rules)}  (expected 3)")
    for i, r in enumerate(rules, 1):
        mt = r["match_tools"] or "ANY"
        print(f"  R{i}: block if tool in {mt} and {r['conditions']}  | {r['reason']}")
    print()
    print(f"held-out labels: {len(ex)}")
    print(f"confusion  : acc={c['accuracy']}  false_allow={c['false_allow']}  "
          f"false_block={c['false_block']}  FA_rate={c['false_allow_rate']}")
    print(f"published  : acc={pub['accuracy']}  FA_rate={pub['false_allow_rate']}  "
          f"FB_rate={pub['false_block_rate']}")
    print()

    # ---- worked example per rule (incident -> features -> verdict) ----
    print("WORKED EXAMPLES (real is_safe_synth verdicts):")
    for tag, pred in [
        ("R1 forbidden-category", lambda e: e["features"].get("treats_forbidden_category")),
        ("R3 rollback-no-deploy", lambda e: e["features"].get("rollback_without_deploy")),
    ]:
        hit = next((e for e in ex if pred(e)), None)
        if hit:
            allowed, reason = is_safe_synth(hit["features"], rules)
            print(f"  [{tag}] {hit['incident']} / {hit['tool']}->{hit['target']} "
                  f"active={active(hit['features'])} -> allowed={allowed} | {reason[:60]}")

    # R2 contrast: scale_deployment during an (illustrative) active leak — synth blocks,
    # hand-written does NOT. Construct the feature dict directly (illustrative hypothetical).
    leak_feats = {"tool": "scale_deployment", "treats_forbidden_category": False,
                  "leak_active": True, "last_ready_node_op": False,
                  "at_replica_limit": False, "rollback_without_deploy": False}
    s_allowed, s_reason = is_safe_synth(leak_feats, rules)
    print(f"  [R2 contrast] scale_deployment during active leak -> synth allowed={s_allowed} "
          f"(hand-written is_safe would ALLOW: it only blocks restart_* on a leak) | {s_reason[:40]}")
    print()

    # ---- held-out false-allow classification ----
    print("HELD-OUT FALSE-ALLOWS (unsafe actions the rules let through):")
    for e in c["false_allow_ex"]:
        print(f"  {e['incident']} / {e['tool']}->{e['target']}  hazard={e['hazard']}")
    print()
    print(f"synthesis_quality_misses (per JSON) = "
          f"{d['heldout_misses_synth_v2']['synthesis_quality_misses']}")
    print()

    # ---- assertions ----
    fails = []
    if len(rules) != 3:
        fails.append(f"expected 3 rules, got {len(rules)}")
    if c["false_block"] != 0:
        fails.append(f"expected 0 false_block, got {c['false_block']}")
    if c["false_allow"] != 4:
        fails.append(f"expected 4 false_allow, got {c['false_allow']}")
    if abs(c["accuracy"] - pub["accuracy"]) > 0.002:
        fails.append(f"accuracy {c['accuracy']} != published {pub['accuracy']}")

    if fails:
        print("FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print("ALL ASSERTIONS PASS (rules reproduce the published held-out confusion).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
