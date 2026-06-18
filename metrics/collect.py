"""Metrics collector — turns simulator output into RCAEval-format CSV.

RCAEval RE1-OB ships with `data.csv` per scenario: 4201 rows × 51 metric columns
(per-service cpu/mem/latency/…) plus `inject_time.txt` (Unix ts). The directory
NAME (`<service>_<faulttype>`) is the ground-truth root-cause label.

We mirror that exactly so:
  - Our offline dataset (incidents_seed.jsonl) and live RCAEval data share a schema.
  - The same `rca_verify.py` (and our `verify/score.py`) can grade both.
  - The `akamai-env/inject_scenario.sh` (cloud) and our `sim/cluster.py` (local)
    produce interchangeable outputs.

CLI:
    python -m metrics.collect --out live-data/cart_oom_kill/<ts> \
        --service cart --fault oom_kill --duration 120
"""
from __future__ import annotations
import json, csv, argparse, time, math, os, sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sim.cluster import ClusterSim, SERVICE_METRICS


# Per-service RCAEval-style metric columns (the 51 columns RCAEval ships with)
# We assemble the full schema as the union of all per-service columns.
def full_schema() -> list[str]:
    cols = ["timestamp", "service", "namespace"]
    for svc_metrics in SERVICE_METRICS.values():
        for m in svc_metrics:
            if m not in cols:
                cols.append(m)
    return cols


def collect(out_dir: Path, service: str, fault: str, duration_s: float = 120.0,
            seed: int = 42, dt: float = 1.0):
    """Run one scenario, write RCAEval-shaped CSV + inject_time.txt."""
    out_dir.mkdir(parents=True, exist_ok=True)

    sim = ClusterSim(seed=seed, duration_s=duration_s)
    sim.boot()
    inc = sim.inject(fault, service=service, duration_s=duration_s)

    # inject_time.txt — Unix ts at the moment of fault injection
    inject_ts = int(time.time())
    (out_dir / "inject_time.txt").write_text(str(inject_ts))

    # manifest.json — what was injected (lets the verifier auto-discover ground truth)
    (out_dir / "manifest.json").write_text(json.dumps(inc.to_dict(), indent=2))

    # data.csv — 51 columns × N rows
    schema = full_schema()
    rows = []
    n_steps = int(duration_s / dt)
    for t_idx in range(n_steps):
        sim.t = t_idx * dt
        snap = sim.metrics_snapshot()
        for row in snap["rows"]:
            r = {c: row.get(c) for c in schema}
            rows.append(r)

    with open(out_dir / "data.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=schema, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  wrote {out_dir}/data.csv  ({len(rows)} rows × {len(schema)} cols)")
    print(f"  inject_time: {inject_ts}  ({datetime.fromtimestamp(inject_ts).isoformat()})")
    return out_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output directory (e.g. live-data/cart_oom_kill/<ts>)")
    ap.add_argument("--service", required=True, help="service to inject into (e.g. cart)")
    ap.add_argument("--fault", required=True,
                    help="fault type (e.g. oom_kill, latency_spike, cpu_saturation, "
                         "bad_deploy_errors, memory_leak, db_pool_exhaustion, "
                         "consumer_lag, dns_failure, cert_expiry, disk_pressure, "
                         "crashloop, stuck_rollout, cache_stampede, upstream_5xx, node_not_ready)")
    ap.add_argument("--duration", type=float, default=120.0)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    collect(Path(args.out), args.service, args.fault, args.duration, args.seed)


if __name__ == "__main__":
    main()
