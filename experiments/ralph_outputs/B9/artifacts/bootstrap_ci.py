#!/usr/bin/env python3
"""B9 — Bootstrap confidence intervals as a robustness check on pass@1.

WHY
---
The pass@k pipeline (rex.eval_pass_at_k / experiments/compute_pass_at_k.py) reports
Wilson score 95% CIs for the pass@1 proportion. Wilson is a closed-form approximation
that assumes each episode is an i.i.d. Bernoulli draw. Our episodes are NOT fully
i.i.d.: they are grouped by incident (5 incidents) and replicated over seeds (3 seeds),
so within an incident the draws are correlated. This script provides a model-free
ROBUSTNESS CHECK: a nonparametric bootstrap (10,000 resamples) over the per-episode
pass/fail outcomes, plus a CLUSTER (block) bootstrap that resamples whole incidents to
respect the grouping. If the bootstrap and cluster-bootstrap intervals broadly agree
with Wilson, the Wilson CIs are trustworthy; where they diverge (esp. the cluster
bootstrap being wider) we learn the i.i.d. assumption is optimistic.

DATA
----
Real per-episode rewards from rex/runs/ablation.json:
  5 conditions x 5 incidents x 3 seeds = 15 episodes / condition.
A reward >= THRESHOLD (0.8) counts as a binary PASS (SLO restored + root cleared).
This is exactly the binary_pass() rule used by the shipped pass@k pipeline, so the
point estimates here match experiments/compute_pass_at_k.py::analyze_ablation().

This script does NOT edit any shared core file. It imports wilson_ci/binary_pass from
the existing single-source-of-truth module for an apples-to-apples comparison; if that
import is unavailable it falls back to a local copy (documented inline).

USAGE
-----
    python3 experiments/ralph_outputs/B9/artifacts/bootstrap_ci.py \
        --resamples 10000 --seed 12345 \
        --out experiments/ralph_outputs/B9/artifacts/bootstrap_ci_results.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]   # .../rl  (artifacts/B9/ralph_outputs/experiments/<rl>)
ABLATION = REPO / "rex" / "runs" / "ablation.json"
THRESHOLD = 0.8
CONDITIONS = ["zero_shot", "best_of_n", "retry_realistic", "rex", "rex_no_oracle"]


# ---- reuse the shipped estimators (single source of truth) -----------------
def _load_reference():
    """Import wilson_ci + binary_pass from experiments/compute_pass_at_k.py.

    Falls back to local definitions if the module can't be imported, so the
    script stays self-contained and runnable. The local copies are byte-for-byte
    the same formulas as the shipped module (verified in 07_test_results.md).
    """
    try:
        sys.path.insert(0, str(REPO / "experiments"))
        from compute_pass_at_k import wilson_ci, binary_pass  # type: ignore
        return wilson_ci, binary_pass, "imported"
    except Exception:  # noqa: BLE001
        def wilson_ci(p, n, z=1.96):
            if n == 0:
                return (0.0, 0.0)
            denom = 1 + z * z / n
            center = (p + z * z / (2 * n)) / denom
            spread = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
            return (max(0.0, center - spread), min(1.0, center + spread))

        def binary_pass(reward, threshold=THRESHOLD):
            return 1 if reward >= threshold else 0

        return wilson_ci, binary_pass, "fallback"


WILSON_CI, BINARY_PASS, REF_SOURCE = _load_reference()


# ---- bootstrap -------------------------------------------------------------
def percentile(sorted_vals, q):
    """Linear-interpolation percentile (q in [0,1]) on a pre-sorted list."""
    if not sorted_vals:
        return 0.0
    if q <= 0:
        return sorted_vals[0]
    if q >= 1:
        return sorted_vals[-1]
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def bootstrap_ci(flat_passes, resamples, rng, alpha=0.05):
    """Nonparametric percentile bootstrap over i.i.d. episode outcomes.

    flat_passes: list[int] of 0/1 per episode.
    Returns (lo, hi, point, n, se).
    """
    n = len(flat_passes)
    point = sum(flat_passes) / n if n else 0.0
    means = []
    for _ in range(resamples):
        s = sum(flat_passes[rng.randrange(n)] for _ in range(n))
        means.append(s / n)
    means.sort()
    lo = percentile(means, alpha / 2)
    hi = percentile(means, 1 - alpha / 2)
    mu = sum(means) / len(means)
    se = math.sqrt(sum((m - mu) ** 2 for m in means) / (len(means) - 1)) if len(means) > 1 else 0.0
    return lo, hi, point, n, se


def cluster_bootstrap_ci(by_incident, resamples, rng, alpha=0.05):
    """Block bootstrap: resample whole incidents (with their seed replicates).

    by_incident: dict incident -> list[int] of 0/1 outcomes (the seeds).
    Respects within-incident correlation; total episode count is held fixed by
    resampling the same NUMBER of incident-blocks each replicate.
    Returns (lo, hi, point, n_blocks, se).
    """
    incidents = list(by_incident.keys())
    nb = len(incidents)
    all_outcomes = [o for inc in incidents for o in by_incident[inc]]
    point = sum(all_outcomes) / len(all_outcomes) if all_outcomes else 0.0
    means = []
    for _ in range(resamples):
        picked = [by_incident[incidents[rng.randrange(nb)]] for _ in range(nb)]
        flat = [o for block in picked for o in block]
        means.append(sum(flat) / len(flat) if flat else 0.0)
    means.sort()
    lo = percentile(means, alpha / 2)
    hi = percentile(means, 1 - alpha / 2)
    mu = sum(means) / len(means)
    se = math.sqrt(sum((m - mu) ** 2 for m in means) / (len(means) - 1)) if len(means) > 1 else 0.0
    return lo, hi, point, nb, se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resamples", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    ap.add_argument("--data", default=str(ABLATION))
    ap.add_argument("--out", default=str(Path(__file__).parent / "bootstrap_ci_results.json"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    data = json.loads(Path(args.data).read_text())
    per_incident = data["per_incident"]
    incidents = data["incidents"]

    out = {
        "source_data": os.path.relpath(args.data, REPO),
        "model": data.get("model"),
        "threshold": args.threshold,
        "resamples": args.resamples,
        "rng_seed": args.seed,
        "reference_estimator_source": REF_SOURCE,
        "n_incidents": len(incidents),
        "metric": "pass@1 (P[reward>=threshold])",
        "conditions": {},
    }

    print(f"{'condition':<18}{'pass@1':>8}{'  Wilson 95%':>20}"
          f"{'  Bootstrap 95%':>22}{'  Cluster-boot 95%':>24}")
    print("-" * 96)

    for cond in CONDITIONS:
        by_inc = {inc: [BINARY_PASS(r, args.threshold) for r in per_incident[cond][inc]]
                  for inc in incidents}
        flat = [o for inc in incidents for o in by_inc[inc]]
        n = len(flat)
        c = sum(flat)
        p1 = c / n if n else 0.0

        w_lo, w_hi = WILSON_CI(p1, n)
        b_lo, b_hi, _, _, b_se = bootstrap_ci(flat, args.resamples, rng)
        cl_lo, cl_hi, _, nb, cl_se = cluster_bootstrap_ci(by_inc, args.resamples, rng)

        out["conditions"][cond] = {
            "n": n, "passes": c, "pass@1": round(p1, 4),
            "wilson95": [round(w_lo, 4), round(w_hi, 4)],
            "bootstrap95": [round(b_lo, 4), round(b_hi, 4)],
            "bootstrap_se": round(b_se, 4),
            "cluster_bootstrap95": [round(cl_lo, 4), round(cl_hi, 4)],
            "cluster_bootstrap_se": round(cl_se, 4),
            "n_blocks": nb,
            "wilson_width": round(w_hi - w_lo, 4),
            "bootstrap_width": round(b_hi - b_lo, 4),
            "cluster_bootstrap_width": round(cl_hi - cl_lo, 4),
        }
        print(f"{cond:<18}{p1:>8.3f}  [{w_lo:.3f},{w_hi:.3f}]"
              f"      [{b_lo:.3f},{b_hi:.3f}]"
              f"        [{cl_lo:.3f},{cl_hi:.3f}]")

    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"\nwrote {os.path.relpath(args.out, REPO)}")
    return out


if __name__ == "__main__":
    main()
