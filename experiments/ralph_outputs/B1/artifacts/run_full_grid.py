#!/usr/bin/env python3
"""B1 — FULL GRID pass@k runner: 42 incidents x 5 conditions x 5 seeds = 1050 episodes.

Task-namespaced wrapper around `rex.eval_pass_at_k.run_eval`. Imports the core
pipeline and EDITS NOTHING (Ralph parallel-safety rules). Writes its result +
crash-survival checkpoint INSIDE experiments/ralph_outputs/B1/artifacts/.

The "full grid" for B1 is:
    incidents  = all 42 (per_family=None)
    conditions = zero_shot, best_of_n, retry_realistic, rex, rex_no_oracle  (5)
    seeds      = 5
=> 42 * 5 * 5 = 1050 model-driven episodes, graded by the P0 deterministic judge.

COMPUTE CAP: a real model run is capped at ~15 min wall by the dispatcher. The full
grid empirically takes ~45 min on glm-5p2 (A1 measured ~2.5s/episode -> 630 eps in
~27 min; 1050 eps scales to ~45 min). To stay honest under the cap, use --per-family
to run a representative subset (same conditions x same 5 seeds, fewer incidents per
family) as a real anchor, while THIS script remains the full, runnable grid: just run
it with --per-family 0 (=all 42) off-cap and it produces the complete 1050-episode JSON.
The .partial checkpoint lets you resume across multiple capped windows toward the full grid.

Usage:
    set -a; source ~/.zshrc; set +a
    # FULL GRID (off-cap, ~45 min, resumable via the .partial checkpoint):
    python3 experiments/ralph_outputs/B1/artifacts/run_full_grid.py --model glm-5p2 --seeds 5
    # representative subset that fits the 15-min cap (2 incidents/family = 6 incidents):
    python3 experiments/ralph_outputs/B1/artifacts/run_full_grid.py \
        --model glm-5p2 --seeds 5 --per-family 2 --out .../subset.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# repo root is 4 levels up: artifacts/B1/ralph_outputs/experiments/<root>
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# import the existing pipeline WITHOUT modifying it
from rex.eval_pass_at_k import THRESHOLD, print_report, run_eval  # noqa: E402

ALL_CONDITIONS = "zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="glm-5p2")
    ap.add_argument("--conditions", default=ALL_CONDITIONS)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--per-family", type=int, default=0,
                    help="incidents per family (0 = ALL 42 = the full grid)")
    ap.add_argument("--max-workers", type=int, default=10)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    per_family = args.per_family or None  # 0 -> None -> all incidents
    tag = "full" if per_family is None else f"sub{args.per_family}"
    out_path = args.out or os.path.join(HERE, f"grid_{tag}_{args.model}.json")
    ckpt = out_path + ".partial"

    out = run_eval(args.model, conditions, per_family=per_family, seeds=args.seeds,
                   max_workers=args.max_workers,
                   label=f"{args.model} ({tag}-grid)", ckpt=ckpt)

    n_incidents = sum(len(v) for v in out["incidents_by_family"].values())
    out["n_incidents"] = n_incidents
    out["grid"] = {
        "incidents": n_incidents, "conditions": conditions, "seeds": args.seeds,
        "episodes": n_incidents * len(conditions) * args.seeds,
        "full_grid": per_family is None and len(conditions) == 5 and args.seeds == 5,
    }

    print_report(out)
    print(f"\ngrid: {n_incidents} incidents x {len(conditions)} conditions x "
          f"{args.seeds} seeds = {out['grid']['episodes']} episodes "
          f"(full_grid={out['grid']['full_grid']})")

    json.dump(out, open(out_path, "w"), indent=2)
    if os.path.exists(ckpt):
        os.remove(ckpt)
    print(f"\n-> {out_path}")
    # floor invariant must always hold (no reward-hacking shortcut)
    assert out["floor_check"]["floor_ok"], "FLOOR LEAK: cheapest path passes threshold"


if __name__ == "__main__":
    main()
