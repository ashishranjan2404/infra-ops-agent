#!/usr/bin/env python3
"""Self-contained validation of the A12 curriculum artifact (no pytest needed)."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
GEN = os.path.join(REPO, "scenarios", "cidg", "generated")
OUT = os.path.join(HERE, "curriculum_order.json")


def run_gen():
    subprocess.run([sys.executable, os.path.join(HERE, "build_curriculum.py")],
                   check=True, capture_output=True)


def main():
    run_gen()
    d = json.load(open(OUT))
    n_yaml = len([f for f in os.listdir(GEN) if f.endswith(".yaml")])
    fails = []

    # 1 validity / coverage
    if not (len(d["order_easy_to_hard"]) == d["n"] == n_yaml):
        fails.append(f"coverage: order={len(d['order_easy_to_hard'])} n={d['n']} yaml={n_yaml}")

    # 2 monotonicity
    diffs = [r["difficulty"] for r in d["incidents"]]
    if diffs != sorted(diffs):
        fails.append("monotonicity: difficulty not non-decreasing")

    # 3 split sanity: simple ranks below cascade/novel
    ranks = {r["family"]: [] for r in d["incidents"]}
    for r in d["incidents"]:
        ranks.setdefault(r["family"], []).append(r["rank"])
    if ranks.get("simple"):
        max_simple = max(ranks["simple"])
        hard = ranks.get("cascade", []) + ranks.get("novel", [])
        if hard and max_simple > min(hard):
            fails.append(f"split: simple max rank {max_simple} > min hard rank {min(hard)}")

    # 4 determinism
    first = open(OUT).read()
    run_gen()
    if open(OUT).read() != first:
        fails.append("determinism: two runs differ")

    # 5 ids unique
    ids = d["order_easy_to_hard"]
    if len(set(ids)) != len(ids):
        fails.append("ids: duplicates present")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print(f"PASS  ({d['n']} incidents, {len(ranks)} families, "
          f"diff range {diffs[0]:.2f}..{diffs[-1]:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
