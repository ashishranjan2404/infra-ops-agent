# 06 — Implementation

## What was built
A standalone, stdlib-only microbenchmark that times `rex.harness.is_safe` against a no-op
baseline and reports the latency distribution + overhead.

### Artifacts (all task-namespaced; NO shared-core edits)
- `artifacts/bench_is_safe.py` — the benchmark. Imports `is_safe` from `rex.harness`
  (adds repo root to `sys.path`, so it runs from any cwd). Builds 6 branch-covering cases,
  asserts each verdict, warms up, times `is_safe` and `_noop` with `perf_counter_ns`,
  computes mean/p50/p99 + overhead delta/ratio, projects a 10-action-plan cost, writes JSON.
- `artifacts/bench_results.json` — the measured numbers from the **full default run**
  (200k timed calls/fn after 20k warmup).
- `artifacts/run.log` — captured stdout of the full run.

### Key design points (from grill + ouroboros)
- **No-op baseline, identical signature** → headline is `is_safe − no-op` (delta + ratio),
  subtracting CPython's call floor and the timer-read overhead.
- **All branches exercised + verdicts asserted** → we time real Layer-1/Layer-2 paths, not a
  degenerate allow path. Verdict mismatch exits 2.
- **Ratio/order-of-magnitude is the portable claim**; absolute µs are host-specific.

## Shared-core changes proposed: NONE
`rex/harness.py` was read-only. `is_safe` already takes `(action, state)` and is pure, so it
needed no shim or refactor to benchmark. No `.patch` is required for this task.

## Measured result (this host, Python 3.13.7)
| fn | mean | p50 | p99 |
|----|------|-----|-----|
| `is_safe` | 0.2704 µs | 0.2500 µs | 0.4160 µs |
| `_noop`   | 0.0528 µs | 0.0420 µs | 0.0840 µs |

- **Overhead vs no-op**: mean **+0.2176 µs**, ratio **5.12×**.
- **Projected per 10-action plan**: **~2.70 µs** total.

## How to reproduce
```
cd /Users/mei/rl
python3 experiments/ralph_outputs/C10/artifacts/bench_is_safe.py
# smoke: python3 .../bench_is_safe.py --iters 5000 --warmup 500 --json /tmp/x.json
```
