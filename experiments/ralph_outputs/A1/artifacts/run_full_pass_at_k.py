#!/usr/bin/env python3
"""A1 — full 42-incident pass@k runner (task-namespaced; imports core, edits nothing).

This is a thin wrapper around `rex.eval_pass_at_k.run_eval` that runs the FULL incident
set (per_family=None -> all 42 incidents) and writes its result + crash-survival
checkpoint INSIDE experiments/ralph_outputs/A1/artifacts/ (never the shared
experiments/results/ dir), per the Ralph parallel-safety rules.

Usage:
    set -a; source ~/.zshrc; set +a
    # full sweep (5 conditions, all 42 incidents):
    python3 experiments/ralph_outputs/A1/artifacts/run_full_pass_at_k.py \
        --model glm-5p2 --seeds 5
    # fast real anchor run (2 conditions, all 42 incidents, fewer seeds):
    python3 experiments/ralph_outputs/A1/artifacts/run_full_pass_at_k.py \
        --model glm-5p2 --seeds 3 --conditions zero_shot,rex
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# repo root is 4 levels up: artifacts/A1/ralph_outputs/experiments/<root>
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# import the existing pipeline WITHOUT modifying it
from rex.eval_pass_at_k import THRESHOLD, print_report, run_eval  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="glm-5p2")
    ap.add_argument("--conditions",
                    default="zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    out_path = args.out or os.path.join(HERE, f"full_pass_at_k_{args.model}.json")
    ckpt = out_path + ".partial"

    # per_family=None  ->  pick_incidents(None)  ->  ALL incidents in every family (42 total)
    out = run_eval(args.model, conditions, per_family=None, seeds=args.seeds,
                   max_workers=args.max_workers, label=f"{args.model} (full-42)", ckpt=ckpt)

    n_incidents = sum(len(v) for v in out["incidents_by_family"].values())
    out["n_incidents"] = n_incidents
    out["full_set"] = True

    print_report(out)
    print(f"\nincidents covered: {n_incidents} "
          f"(simple={len(out['incidents_by_family']['simple'])}, "
          f"cascade={len(out['incidents_by_family']['cascade'])}, "
          f"novel={len(out['incidents_by_family']['novel'])})")

    json.dump(out, open(out_path, "w"), indent=2)
    if os.path.exists(ckpt):
        os.remove(ckpt)
    print(f"\n-> {out_path}")
    assert n_incidents == 42, f"expected 42 incidents, got {n_incidents}"
    assert out["floor_check"]["floor_ok"], "FLOOR LEAK: cheapest path passes threshold"


if __name__ == "__main__":
    main()
