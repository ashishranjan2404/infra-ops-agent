#!/usr/bin/env python3
"""J4 — synthetic MTTR-trial generator (exercises the analysis harness).

Real human-in-the-loop measurement is the documented blocker (you cannot conjure
operators + on-call rotations + a controlled incident replay environment in a
batch job). This generator stands in for that data so the analysis harness is
exercised end-to-end on data with a KNOWN ground-truth effect, which lets us
validate that the statistics recover the planted speedup before any real run.

Grounding: baseline (unassisted) MTTRs are seeded from the A9 mttr_labels real
incidents where available (so the right-skew / scale matches real outages); for
incidents without a real label we draw from a lognormal fit to the labeled ones.
The agent-assisted arm applies a multiplicative speedup with operator-level
random effects + per-trial noise — i.e. agent help is heterogeneous, not a
constant factor. A configurable fraction of incidents get NO benefit (the agent
is a wash on novel/hard incidents) so the planted effect is realistic, not ideal.

Outputs a trials CSV consumable by mttr_analysis.py for either design:
  --design within  -> emits paired rows (same incident, both arms, shared pair_id)
  --design between -> emits randomized independent rows (A/B)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random

_A9_JSON = os.path.join(os.path.dirname(__file__), "..", "..", "A9",
                        "artifacts", "mttr_labels.json")


def _load_a9_baseline() -> list[float]:
    """Return real-incident MTTRs (minutes) from A9 labels, if the file exists."""
    try:
        with open(os.path.normpath(_A9_JSON)) as f:
            data = json.load(f)
        vals = [inc["mttr_minutes"] for inc in data["incidents"]
                if inc.get("mttr_minutes") not in (None, "", "null")]
        return [float(v) for v in vals if float(v) > 0]
    except Exception:
        return []


def _lognormal_params(vals: list[float]):
    logs = [math.log(v) for v in vals]
    mu = sum(logs) / len(logs)
    var = sum((x - mu) ** 2 for x in logs) / max(len(logs) - 1, 1)
    return mu, math.sqrt(var)


def simulate(n_incidents: int, design: str, *, true_speedup: float,
             no_benefit_frac: float, operator_sd_log: float, trial_sd_log: float,
             seed: int):
    rng = random.Random(seed)
    base_vals = _load_a9_baseline()
    used_a9 = bool(base_vals)
    if base_vals:
        mu, sd = _lognormal_params(base_vals)
    else:
        mu, sd = math.log(120), 0.8  # fallback prior: ~2h median, heavy tail

    rows = []
    n_operators = max(4, n_incidents // 5)
    # operator-level random effect on how much the agent helps THAT operator
    op_effect = {f"op{j}": rng.gauss(0, operator_sd_log) for j in range(n_operators)}

    for i in range(n_incidents):
        # baseline (unassisted) MTTR: reuse a real A9 value when we can, else draw
        if base_vals and rng.random() < 0.5:
            baseline = rng.choice(base_vals) * math.exp(rng.gauss(0, 0.15))
        else:
            baseline = math.exp(rng.gauss(mu, sd))
        baseline = max(baseline, 1.0)

        operator = f"op{rng.randrange(n_operators)}"
        # does the agent help on this incident at all?
        if rng.random() < no_benefit_frac:
            eff_speedup = math.exp(rng.gauss(0, trial_sd_log))  # ~no net effect
        else:
            log_su = (math.log(true_speedup) + op_effect[operator]
                      + rng.gauss(0, trial_sd_log))
            eff_speedup = max(math.exp(log_su), 0.2)  # never magic instant fix
        assisted = max(baseline / eff_speedup, 1.0)

        inc_id = f"sim-inc-{i:03d}"
        if design == "within":
            pid = f"pair-{i:03d}"
            rows.append(dict(incident_id=inc_id, arm="control", mttr_minutes=round(baseline, 2),
                             pair_id=pid, operator_id=operator, resolved=True))
            rows.append(dict(incident_id=inc_id, arm="agent", mttr_minutes=round(assisted, 2),
                             pair_id=pid, operator_id=operator, resolved=True))
        else:  # between: randomize incident to one arm only
            arm = "control" if rng.random() < 0.5 else "agent"
            mttr = baseline if arm == "control" else assisted
            rows.append(dict(incident_id=inc_id, arm=arm, mttr_minutes=round(mttr, 2),
                             pair_id="", operator_id=operator, resolved=True))
    return rows, used_a9


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="J4 synthetic MTTR trial generator")
    ap.add_argument("--n", type=int, default=40, help="number of incidents")
    ap.add_argument("--design", choices=["within", "between"], default="within")
    ap.add_argument("--true-speedup", type=float, default=1.8,
                    help="planted geometric-mean speedup (control/agent)")
    ap.add_argument("--no-benefit-frac", type=float, default=0.25,
                    help="fraction of incidents where agent gives ~no benefit")
    ap.add_argument("--operator-sd-log", type=float, default=0.25)
    ap.add_argument("--trial-sd-log", type=float, default=0.30)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="-", help="output CSV path or - for stdout")
    args = ap.parse_args(argv)

    rows, used_a9 = simulate(args.n, args.design, true_speedup=args.true_speedup,
                             no_benefit_frac=args.no_benefit_frac,
                             operator_sd_log=args.operator_sd_log,
                             trial_sd_log=args.trial_sd_log, seed=args.seed)
    cols = ["incident_id", "arm", "mttr_minutes", "pair_id", "operator_id", "resolved"]
    import sys
    f = sys.stdout if args.out == "-" else open(args.out, "w", newline="")
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
    if args.out != "-":
        f.close()
    print(f"# wrote {len(rows)} rows ({args.design}); A9 baseline used: {used_a9}; "
          f"planted speedup={args.true_speedup}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
