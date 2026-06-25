# 04 — Technical Spec

## Target under test
`rex.harness.is_safe(action: dict, state: dict) -> tuple[bool, str]`
- Pure function. Reads `action["tool"]`, `action["args"]["target"]`, and several keys of
  `state` (`forbidden_categories`, `gold_category`, `mem_leak_active`,
  `draining_last_ready_node`, `at_replica_limit`, `recent_deploy`, `incident`).
- Returns `(allowed: bool, reason: str)`.

## Script: `artifacts/bench_is_safe.py`

### Functions / signatures
- `_noop(action, state) -> tuple[bool, str]` — baseline; returns `(True, "")`.
- `_build_cases() -> list[tuple[dict, dict, bool]]` — `(action, state, expected_allowed)`.
- `_time_calls(fn, cases, iters) -> list[float]` — per-call latency in **µs**
  (via `time.perf_counter_ns`, ns→µs), cycling cases by `i % len(cases)`.
- `_stats(lat_us) -> dict` — `{n, mean_us, p50_us, p99_us, min_us, max_us, stdev_us}`
  (percentiles via sorted-index `s[int(q*(n-1))]`).
- `main()` — parse args, sanity-check verdicts, warmup, time both fns, compute overhead, write JSON.

### Workload cases (6)
| # | tool | state highlight | expected | branch |
|---|------|-----------------|----------|--------|
| 1 | modify_network_policy | gcp forbidden set | allowed | fast path |
| 2 | scale_deployment | saturation forbidden | blocked | Layer-1 |
| 3 | rollback_deployment | bad_deploy forbidden | blocked | Layer-1 |
| 4 | restart_pod | mem_leak_active=True | blocked | Layer-2 |
| 5 | drain_node | draining_last_ready_node=True | blocked | Layer-2 |
| 6 | restart_service | nothing forbidden/active | allowed | Layer-2 pass-through |

### CLI
`--iters` (default 200000), `--warmup` (default 20000), `--json` (default `bench_results.json`).

### Output JSON contract (`bench_results.json`)
```json
{
  "python": "3.13.7",
  "iters": 200000, "warmup": 20000, "n_cases": 6,
  "is_safe":        {"n":N,"mean_us":..,"p50_us":..,"p99_us":..,"min_us":..,"max_us":..,"stdev_us":..},
  "noop_baseline":  {"n":N,"mean_us":..,"p50_us":..,"p99_us":..,...},
  "overhead_mean_us": <is_safe.mean - noop.mean>,
  "overhead_p99_us":  <is_safe.p99 - noop.p99>,
  "overhead_ratio_mean": <is_safe.mean / noop.mean>,
  "projected_cost_per_10action_plan_us": <is_safe.mean * 10>
}
```

### Test cases / validation
1. **Syntax**: `python3 -m ast` parse → OK.
2. **Verdict sanity**: every case's `is_safe` verdict == `expected`; else exit 2 (guards against
   timing a degenerate path / harness drift).
3. **Smoke run**: `--iters 5000 --warmup 500` completes, writes JSON, exit 0.
4. **Full run**: default iters; mean/p50/p99 present and finite for both fns; overhead > 0.

### Determinism / portability
Stdlib only. No network/model/sim. Adds repo root to `sys.path` so it runs from any cwd.
Absolute numbers are machine-dependent (microbench); the **ratio** and the
**order-of-magnitude verdict** are the stable, portable conclusions.
