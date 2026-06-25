# SUMMARY — C10: Harness inference latency (does `is_safe` add meaningful overhead?)

## Question
Does `rex.harness.is_safe` — the per-action safety gate called once per planned action in
`run_plan` — add meaningful latency to harness inference?

## What was done
Built and ran a real, stdlib-only microbenchmark (`artifacts/bench_is_safe.py`) that times
`is_safe` over 200k calls across a 6-case workload covering every branch (allow fast-path,
two Layer-1 category blocks, two Layer-2 state traps), with verdict assertions, against a
no-op baseline of identical signature. Reports mean/p50/p99 + overhead delta/ratio.

## Result (Python 3.13.7, this host)
| fn | mean | p50 | p99 |
|----|------|-----|-----|
| `is_safe` | **0.2704 us** | 0.2500 us | 0.4160 us |
| `_noop`   | 0.0528 us | 0.0420 us | 0.0840 us |

- Overhead vs no-op: **+0.2176 us mean, 5.12x**.
- Projected per 10-action plan: **~2.7 us**.

## Verdict
**No meaningful overhead.** `is_safe` is sub-microsecond per call; even amortized over a full
plan it is ~2.7 us — roughly 10^4–10^7x smaller than the sim tick / LLM plan-generation it sits
beside in `run_plan`. It is in the noise of harness inference latency. The 5x ratio over a no-op
is real but applies to a vanishingly small base.

## Honest caveats
- Scoped to `is_safe` (not `is_safe + build_state`); `build_state` is adjacent context, unmeasured.
- Sub-us microbench → the **delta/ratio** is trustworthy, the raw mean partly reflects timer
  overhead; p99/max are scheduler-bound, not function behavior. Absolute us are host-specific.
- Magnitude-vs-sim claim is reasoned, not co-measured end-to-end (named follow-up in 09).

## Artifacts
- `artifacts/bench_is_safe.py` — benchmark (runnable, syntax-checked, exits 0).
- `artifacts/bench_results.json` — full-run numbers.
- `artifacts/run.log` — captured stdout.

## Shared-core edits: NONE (rex/harness.py read-only; all writes under C10/).
