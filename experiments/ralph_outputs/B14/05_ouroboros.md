# B14 — Ouroboros (self-critique as 3 different engineers)

## Engineer 1 — Correctness / data-contract pedant
**Found problems:**
- `n_incidents` for A2 (`deepseek-v4-pro`) is `null` in the JSON. If I read it blindly I'd crash
  or report 0. → **Fixed:** `n_incidents()` falls back to summing `incidents_by_family`
  (yields 30 for A2). Verified in the run output (`n_incidents=30`).
- A row could have `pass@1` missing for a condition. → Guarded: skip rows where `pass@1 is None`.
- Division by zero if a condition somehow had 0 cost. → Guarded with `cost_per_inc > 0`.
**Remaining:** the schema is assumed stable across A* artifacts; a differently-shaped result JSON
(e.g. no `by_condition`) silently yields no rows for that file. Acceptable — `.get` defaults make
it skip, not crash. Documented.

## Engineer 2 — "is the cost model actually right?" skeptic
**Found problems:**
- `retry_realistic` real cost is 1..N with early-exit; my 2.3 is an assumed *expected* value, not
  derived from the data. The result JSONs don't log how many retries fired. → **Accepted as a
  documented assumption** (named `RETRY_EXPECTED_CALLS`). Honest: this is the one condition whose
  call count I can't pin exactly. Flagged in cost_model.py docstring and in the critique.
- `best_of_n` and `rex` both cost exactly N here, so they're indistinguishable on cost — but `rex`
  gets 0.90 pass@1 vs best_of_n 0.34. That's the whole point: **same cost, dramatically different
  pass@1 ⇒ rex dominates best_of_n on cost-efficiency.** This is a real, defensible finding, not a
  bug. Good.
- Over-engineering check: do I need `output_token_utilization` at all? Yes — without it the
  absolute $ is a strict worst-case (max_tokens fully used), which overstates cost ~1.7x. Keeping
  it, default 0.6, documented. Not gold-plating.

## Engineer 3 — reviewer-hostile / "what's the headline lie?"
**Found problems:**
- The "pass@1 per $" numbers (e.g. 89.64) look impressively precise for an *estimate*. A reviewer
  could mistake them for measured. → **Mitigated:** table header says **ESTIMATED** in bold,
  every row carries `price_assumed`, and the JSON `cost_basis` field spells it out. Numbers are
  ratios of estimates — I won't pretend otherwise.
- The "most cost-efficient = zero_shot" row could be read as "REx isn't worth it." That's the
  reviewer trap PSRE warned about. → **Addressed in critique:** zero_shot wins $/pass only because
  it's cheapest, but it leaves 77% of incidents unresolved. The honest read is *rex is the
  efficient frontier point at high pass@1* (87.31 per $, essentially matching zero_shot's 89.64 at
  4x the absolute pass rate). I add this interpretation to 08/09 rather than letting the bare
  table mislead.

## Final filtered spec (delta from 04)
- Keep all guards (null n_incidents, missing pass@1, zero cost).
- `RETRY_EXPECTED_CALLS` explicitly labelled the one un-pinnable call count.
- Add interpretation note (zero_shot $/pass is a floor-cost artifact; rex is the high-pass
  frontier) to 08_verification and 09_critique.
- No new code complexity added — all three engineers' fixes were already in the implementation or
  are doc-level.
