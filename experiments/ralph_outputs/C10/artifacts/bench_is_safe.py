#!/usr/bin/env python3
"""Benchmark harness inference latency: does rex.harness.is_safe add meaningful overhead?

is_safe(action, state) is the per-action safety gate in rex/harness.py. It is called
once per planned action inside run_plan, so its latency multiplies by the number of
actions in every evaluated trajectory. This script measures that cost in isolation.

We time is_safe over many calls across a representative mix of inputs (allowed actions,
Layer-1 category blocks, Layer-2 state-conditional traps) and compare it against a no-op
baseline (a trivial function with the same call signature) to isolate the work is_safe
does from Python's raw call/dispatch overhead.

Outputs (stdout + --json file):
  mean / p50 / p99 latency per call for is_safe and the no-op, plus the overhead delta.

Pure-CPU, deterministic, no network / no model. Run from repo root:
  python3 experiments/ralph_outputs/C10/artifacts/bench_is_safe.py
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time

# Allow running from anywhere: add repo root (4 levels up) to sys.path.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from rex.harness import is_safe  # noqa: E402


def _noop(action, state):
    """Baseline: same signature as is_safe, returns the same shape, does ~nothing.
    Isolates Python call/dispatch + tuple-build cost from is_safe's real logic."""
    return (True, "")


# A representative workload: each case exercises a different code path in is_safe.
# (action_dict, state_dict, expected_allowed)
def _build_cases():
    base_state = {
        "incident": "gcp_service_control",
        "forbidden_categories": ["bad_deploy", "resource_exhaustion", "node_failure", "saturation"],
        "gold_category": "config_error",
        "mem_leak_active": False,
        "draining_last_ready_node": False,
        "at_replica_limit": False,
        "recent_deploy": True,
    }
    return [
        # allowed: fix tool for this incident, hits the fast path to (True, "")
        ({"tool": "modify_network_policy", "args": {"target": "service-control"}},
         dict(base_state), True),
        # Layer-1 category block: scale_deployment treats 'saturation' (forbidden here)
        ({"tool": "scale_deployment", "args": {"target": "service-control"}},
         dict(base_state), False),
        # Layer-1 category block: rollback treats 'bad_deploy' (forbidden here)
        ({"tool": "rollback_deployment", "args": {"target": "workspace"}},
         dict(base_state), False),
        # Layer-2 trap: restart while a mem leak is active
        ({"tool": "restart_pod", "args": {"target": "image-resizer"}},
         {**base_state, "forbidden_categories": [], "mem_leak_active": True}, False),
        # Layer-2 trap: drain the last Ready node
        ({"tool": "drain_node", "args": {"target": "worker-node-1"}},
         {**base_state, "forbidden_categories": [], "draining_last_ready_node": True}, False),
        # allowed generic action: restart with no active leak, nothing forbidden
        ({"tool": "restart_service", "args": {"target": "edge-api"}},
         {**base_state, "forbidden_categories": [], "mem_leak_active": False}, True),
    ]


def _time_calls(fn, cases, iters):
    """Call fn(action, state) iters times cycling through cases; return per-call
    latencies in microseconds. perf_counter_ns avoids float granularity issues."""
    ncases = len(cases)
    lat_us = []
    append = lat_us.append
    pc = time.perf_counter_ns
    for i in range(iters):
        action, state, _ = cases[i % ncases]
        t0 = pc()
        fn(action, state)
        append((pc() - t0) / 1000.0)  # ns -> us
    return lat_us


def _stats(lat_us):
    s = sorted(lat_us)
    n = len(s)
    return {
        "n": n,
        "mean_us": statistics.fmean(s),
        "p50_us": s[int(0.50 * (n - 1))],
        "p99_us": s[int(0.99 * (n - 1))],
        "min_us": s[0],
        "max_us": s[-1],
        "stdev_us": statistics.pstdev(s),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=200_000,
                    help="timed calls per function (default 200k)")
    ap.add_argument("--warmup", type=int, default=20_000,
                    help="untimed warmup calls per function (default 20k)")
    ap.add_argument("--json", default=os.path.join(_HERE, "bench_results.json"))
    args = ap.parse_args()

    cases = _build_cases()

    # Correctness sanity: confirm the workload exercises the intended branches before timing.
    mismatches = []
    for action, state, expected in cases:
        allowed, _reason = is_safe(action, state)
        if allowed != expected:
            mismatches.append({"tool": action["tool"], "expected": expected, "got": allowed})
    if mismatches:
        print("WORKLOAD MISMATCH (branches not as expected):", mismatches, file=sys.stderr)
        return 2

    # Warmup (JIT-free CPython, but warms caches / import-time globals).
    _time_calls(is_safe, cases, args.warmup)
    _time_calls(_noop, cases, args.warmup)

    safe_lat = _time_calls(is_safe, cases, args.iters)
    noop_lat = _time_calls(_noop, cases, args.iters)

    safe = _stats(safe_lat)
    noop = _stats(noop_lat)
    overhead_mean = safe["mean_us"] - noop["mean_us"]
    overhead_p99 = safe["p99_us"] - noop["p99_us"]

    out = {
        "python": sys.version.split()[0],
        "iters": args.iters,
        "warmup": args.warmup,
        "n_cases": len(cases),
        "is_safe": safe,
        "noop_baseline": noop,
        "overhead_mean_us": overhead_mean,
        "overhead_p99_us": overhead_p99,
        "overhead_ratio_mean": (safe["mean_us"] / noop["mean_us"]) if noop["mean_us"] else None,
        # context: a typical evaluated plan applies <=10 actions; project the aggregate cost.
        "projected_cost_per_10action_plan_us": safe["mean_us"] * 10,
    }

    with open(args.json, "w") as f:
        json.dump(out, f, indent=2)

    print(f"python {out['python']}  iters={args.iters}  cases={len(cases)}")
    print(f"is_safe : mean={safe['mean_us']:.4f}us  p50={safe['p50_us']:.4f}us  "
          f"p99={safe['p99_us']:.4f}us")
    print(f"no-op   : mean={noop['mean_us']:.4f}us  p50={noop['p50_us']:.4f}us  "
          f"p99={noop['p99_us']:.4f}us")
    print(f"overhead: mean={overhead_mean:.4f}us  p99={overhead_p99:.4f}us  "
          f"ratio={out['overhead_ratio_mean']:.2f}x")
    print(f"projected per 10-action plan: {out['projected_cost_per_10action_plan_us']:.2f}us")
    print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
