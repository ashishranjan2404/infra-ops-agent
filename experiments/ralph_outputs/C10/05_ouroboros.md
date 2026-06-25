# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — "Measurement Methodologist"
**Problems found:**
1. Timing each call individually with `perf_counter_ns` adds per-iteration timer-read overhead
   that, for a sub-µs function, is a non-trivial fraction of the measurement. The no-op baseline
   *partially* cancels this (same timer pattern), so the **overhead delta** is more trustworthy
   than either absolute mean. → Must state explicitly that the **delta/ratio** is the headline,
   not the raw `is_safe` mean.
2. p99 of a sub-µs call is dominated by OS preemption, not the function. → Must caveat, not boast.
3. No control for CPU frequency scaling / thermal. → Acceptable for an order-of-magnitude claim;
   document as a limitation rather than fix (turbo-pinning is out of scope for this task).

**Filtered:** keep per-call timing (simple, the delta cancels apparatus bias), but headline the
**ratio + delta**, caveat p99, document freq-scaling as a known limitation.

## Engineer B — "Scope Skeptic"
**Problems found:**
1. The benchmark omits `build_state`, which `run_plan` actually calls every action. Is the
   "overhead" claim then incomplete? → **Decided in 03**: task scope is `is_safe` vs no-op. We
   note `build_state` as adjacent context in 09, not in the headline. Not a gap — a scoped choice.
2. Workload is 6 hand-picked cases; real plans skew toward allow paths. Does the case mix bias
   the mean? → The per-branch cost differs by only a few dict ops; the mix barely moves the mean.
   But to be honest we cycle uniformly and **state the mix** so the number is interpretable.
3. `forbidden_categories` here is a small list (≤4). If it ever grows large, the `in` test goes
   linear. The benchmark wouldn't catch that regression unless re-parameterized. → Document as a
   **regression-guard caveat**: this benchmark fixes list size; a separate scaling sweep would be
   needed to catch O(n) blowups. Out of scope but named.

**Filtered:** keep scope as-is (justified), state the case mix and the small-list assumption.

## Engineer C — "Reproducibility Auditor"
**Problems found:**
1. Absolute µs numbers won't reproduce on a different machine → reader might think the artifact
   is "wrong" on rerun. → Emphasize the **ratio** and **order-of-magnitude verdict** as the
   portable claim; absolute numbers are illustrative of *this* host.
2. JSON path defaults next to the script — fine, but a stale `bench_results.json` from a smoke
   run could be mistaken for the full run. → The committed `bench_results.json` is from the
   **full default run**; the smoke run writes to `/tmp` (see 07), so the artifact is the real one.
3. No record of host/CPU. → `python` version is captured; full host specs are overkill for an
   order-of-magnitude latency claim. Documented as a minor limitation.

**Filtered:** keep, with explicit "ratio is the portable claim" framing and confirmation that the
committed JSON is the full run.

## Final filtered spec (deltas applied to 04)
- Headline = **overhead delta + ratio** (not raw mean); p99 explicitly caveated as apparatus-bound.
- Document: case mix, small-`forbidden_categories` assumption, freq-scaling, host-dependence.
- Committed `bench_results.json` = full default run; smoke run isolated to `/tmp`.
- No code change required beyond what 04 already specifies — the script already emits delta+ratio
  and the projected per-plan cost; the refinements are interpretive/documentation.
