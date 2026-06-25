# 09 — Honest Critique

## What's weak / what a reviewer attacks
1. **Scoped to `is_safe` alone, not the full per-action gate path.** `run_plan` calls
   `is_safe(a, build_state(...))` every action, and `build_state` allocates a fresh dict each
   call. I deliberately excluded `build_state` from the headline (task wording = "is_safe" + "no-op";
   see 02/03 RLE-vs-SMR debate). A reviewer could fairly say the *real* per-action safety cost is
   `is_safe + build_state`. **Adjacent context**: `build_state` is also pure Python dict
   construction (~handful of `.get`/membership ops + one `set`-ish derivation), almost certainly
   another sub-µs cost — but I did not measure it, so I will not assert a number. This is the
   honest boundary of the deliverable.
2. **Microbenchmark of a sub-µs function is intrinsically noisy.** Per-call `perf_counter_ns`
   reads cost a meaningful fraction of the measured value. I mitigate with a no-op baseline (the
   delta cancels most apparatus bias) and large iters, but the absolute `is_safe` mean is partly
   timer overhead. The **delta/ratio** is the trustworthy figure, not the raw mean.
3. **p99 / max are apparatus-bound.** `is_safe` max = 80 µs is one scheduler-preemption sample,
   not function behavior. I report it but explicitly do not interpret it as "is_safe is sometimes
   slow." A skeptic who fixates on max would be misreading the data.
4. **Host-specific absolutes.** Numbers won't reproduce exactly elsewhere. Only the **order of
   magnitude** (sub-µs) and the **ratio** (~5×) are portable claims.
5. **Fixed `forbidden_categories` size.** The Layer-1 `cat in forbidden_categories` test is O(n)
   in the list length. Here n≤4, so it's flat. The benchmark does **not** sweep n, so it would
   not catch a future regression where that list grew large. A scaling sweep is the obvious
   follow-up but is out of scope for "measure the latency."
6. **No comparison run against the actual sim step.** I assert the sim/LLM step is 10^4–10^7×
   larger from architecture knowledge (it does `World.from_spec` + ticks + upstream model calls),
   not from a measured side-by-side in this artifact. The verdict's *magnitude* claim leans on
   that reasoning rather than a co-measurement. A stronger version would time `run_plan` end-to-end
   and show is_safe's share directly.

## What's missing / negative results
- No end-to-end `run_plan` profile attributing % time to `is_safe` (would make the "noise" claim
  airtight). Not blocked — just scoped out to keep the deliverable focused.
- No `build_state` timing (scoped out, see #1).

## Net honest assessment
The core question is answered with real data: `is_safe` is sub-µs per call, ~5× a no-op but
~2.7 µs over a 10-action plan — negligible next to the sim/LLM step. The result is robust to the
caveats above (all of which push the absolute number *down*, not up). The main legitimate gap is
the absence of a direct end-to-end attribution, which would upgrade the magnitude claim from
"reasoned" to "measured."
