# A14 — 05 Ouroboros (3 self-critiques in sequence)

## Engineer A — "the boundary semantics are sloppy"
**Problem found**: The spec says "pre-flight: start only if not over budget", which means the
iteration that *crosses* the line still runs. With `time_budget_s=5` and `5s/call`, the first
call brings `cum=5 >= 5`, and the SECOND is refused — so a budget of "5s" actually buys exactly
ONE call, not "as many as fit in 5s". That's a footgun: a naive reader sets `time_budget_s` to
the total time they want and gets one fewer call than expected near the boundary.
**Resolution**: This is intentional and documented as "you finish the action you started, then
the clock stops you" — the realistic SRE semantics. But I added the exact arithmetic to the demo
comments and tests (e.g. `5s budget, 5s/call -> 1 call`) so the boundary is unambiguous, not
surprising. Kept the soft-ceiling-at-boundary rule.

## Engineer B — "raising inside the proposer can corrupt the loop / lose work"
**Problem found**: `refine_loop` doesn't expect its `propose_fn` to raise. If it raises on
iteration 3, the `for i in range(budget)` aborts and the function never returns — so the
loop's own aggregation (`best_score`, etc.) is lost. The wrapper must reconstruct that, and if
reconstruction drifts from the real loop's logic, a truncated episode reports inconsistent
numbers vs a non-truncated one.
**Resolution**: Mitigated by capturing each iteration through the loop's existing `log=` hook
(every completed iteration is logged *before* the next propose call), then rebuilding the
result in `_result_from_iterations` using the SAME aggregation as `rex.loop.refine_loop`
(best = argmax score; clean_win = any iter with no failed_checks; outcome map). Verified by
test 4 (truncated episode still yields a coherent result with the kept iteration).

## Engineer C — "the time axis is untestable / hardware-coupled, and steps are too coarse"
**Problem found**: (a) Default time = real wall-clock makes any CI flaky. (b) Step cost treats
a cheap `restart_pod` and a dangerous `drain_node` as equal cost — understating risk.
**Resolution**: (a) Solved by the injectable `cost_fn` / `clock` — every test uses a fixed
fake cost, zero wall-clock dependence; real latency is only the *default* for live runs.
(b) Acknowledged as a real limitation (logged in 09_critique): per-action *risk weighting* is a
clean v2 (`cost_fn` could be generalized to `action_cost_fn(action)->float`). For v1 we keep
uniform step cost — it's the honest minimal model and the time axis already captures "slow =
expensive". Not over-engineering now.

## Final filtered spec deltas
- Documented the soft-ceiling boundary arithmetic explicitly (A).
- Lossless iteration capture via `log=` + aggregation mirror (B).
- Injectable deterministic cost; uniform step cost in v1 with risk-weighting noted as v2 (C).
