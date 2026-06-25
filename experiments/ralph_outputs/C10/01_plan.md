# 01 — Plan: C10 Measure harness inference latency (does is_safe add meaningful overhead?)

## Objective
Quantify the per-call latency of `rex.harness.is_safe(action, state)` — the safety gate
called once per planned action inside `run_plan` — and determine whether it adds
*meaningful* overhead to harness inference. "Meaningful" is judged against (a) a no-op
baseline (raw Python call/dispatch cost) and (b) the real dominant cost in this project:
the LLM/sim step, which is orders of magnitude larger.

## Grounding (read of `rex/harness.py`)
- `is_safe(action, state)` (lines 325–356) is a **pure function**: no I/O, no model, no
  global mutation. It does:
  - dict `.get` lookups on `action` / `args`,
  - one `TOOL_TREATS` dict lookup + membership test against `state["forbidden_categories"]`
    (Layer-1 category block),
  - up to four `tool in (...)` + state-flag checks (Layer-2 traps),
  - returns a `(bool, str)` tuple.
- It is invoked in `run_plan` (line 398): `ok, reason = is_safe(a, build_state(...))` —
  **once per action** in the plan. So total contribution = (per-call latency) × (#actions).
- Therefore the right metric is per-call latency, and the right framing is "× #actions per
  trajectory vs the cost of the sim/LLM step it sits next to."

## Approach
1. Write a standalone benchmark script (`artifacts/bench_is_safe.py`) that:
   - Builds a representative workload of ~6 cases exercising every branch (allowed fast
     path, Layer-1 block ×2, Layer-2 traps ×2, allowed generic).
   - Sanity-checks each case returns the expected allowed/blocked verdict (so we're timing
     real branches, not a degenerate path).
   - Warms up, then times `is_safe` over many iterations with `perf_counter_ns`.
   - Times a `_noop(action, state)` baseline with the same signature for overhead isolation.
   - Reports mean / p50 / p99 (µs) for both, plus overhead delta and ratio, and a projected
     cost for a 10-action plan.
   - Writes `bench_results.json`.
2. Run it for real from repo root. Record output in `run.log`.

## Files to create (all task-namespaced; NO shared-core edits)
- `experiments/ralph_outputs/C10/artifacts/bench_is_safe.py` — benchmark.
- `experiments/ralph_outputs/C10/artifacts/bench_results.json` — measured numbers.
- `experiments/ralph_outputs/C10/artifacts/run.log` — captured stdout.
- The 10 step docs + SUMMARY.md + result.json.

## Files to modify
None. `rex/harness.py` is read-only for this task; we only import `is_safe`.

## Dependencies
Python 3.13 stdlib only (`time`, `statistics`, `json`). No HUD/network/model needed —
this is a pure-CPU microbenchmark, fully runnable offline.

## Risks
- **Microbenchmark noise**: sub-µs timings are sensitive to scheduler jitter → mitigate
  with warmup, large iter count, and reporting p50/p99 not just mean.
- **`perf_counter_ns` granularity** dominating a sub-µs call → mitigate by trusting the
  aggregate distribution rather than any single sample; the no-op baseline calibrates the
  measurement floor.
- **Unrepresentative workload** (only timing the fast path) → mitigate by cycling all
  branches and asserting verdicts.

## Success criteria
- Script runs for real, reports mean/p50/p99 for `is_safe` and the no-op.
- Overhead vs no-op quantified (delta + ratio).
- A defensible verdict on "meaningful overhead?" grounded in the per-call number and its
  multiple relative to the surrounding sim/LLM cost.
