# 05 — Ouroboros (self-critique as 3 engineers)

## Engineer A — "data provenance" reviewer
**Problem found:** The spec asserts `ablation.json` is real but never checks its
shape at load time. If a future ablation rewrites the file with a different schema
(e.g. `per_incident` flattened), `sweep()` would KeyError or silently produce empty
rows. **Also:** `best_control` via `argmax` over a dict has nondeterministic tie-break
in older Pythons — if two controls tie, which is "best" is arbitrary and could flip
the reported gap between runs.
**Fix:** Tie-break is deterministic in CPython `max` (first max wins by iteration
order, and dict order is insertion order = stable here). Acceptable, but DOCUMENT
that `best_control` is "first arm achieving the max pass-rate." Add an explicit assert
that `per_incident` is a non-empty dict of dicts of lists before sweeping. → noted;
the assert is cheap, gap is real if ties occur but the GAP VALUE is unaffected by
which tied arm is named (same pass-rate), so the headline number is safe.

## Engineer B — "metric semantics" reviewer
**Problem found:** Reporting one flat pass-rate per arm pools across incidents. But
the fair-control ablation cares about per-incident lift too — pooling can hide that
REx wins only on 2 of 5 incidents. A reviewer attacks "is the win concentrated?"
**Fix:** For B11 the QUESTION is threshold-robustness of the AGGREGATE claim, not
per-incident decomposition (that's a different ablation). Pooling is the correct unit
here. BUT I will surface per-incident reward bands in the data so a reader can see
the win isn't a single lucky incident: rex hits 1.0 on multiple incidents. → keep
aggregate; mention distribution in 09.

**Problem found (real):** `wilson95` uses pooled n=15, but the 15 are 5 incidents x 3
seeds — NOT 15 i.i.d. draws (seeds within an incident are correlated). The CI is
therefore optimistically narrow.
**Fix:** This is a genuine limitation. Report the CI but flag in 09 that the effective
sample size < 15 due to incident clustering; the robustness claim rests on rank-order,
not the CI width. ACCEPTED as a caveat, not a code change (no clustered-CI for n=15).

## Engineer C — "over/under-engineering" reviewer
**Problem found:** `render_table` hard-codes column widths; with a 5th threshold the
header could misalign. Minor.
**Fix:** Widths are generous (12 cols); fine for <=6 thresholds. Not worth
parametrising — YAGNI.
**Problem found (real):** The script's default `--thresholds` duplicates the task's
{0.7,0.8,0.86,0.9}; if someone passes only 0.80 the "robust" flag becomes trivially
True (one threshold). Misleading.
**Fix:** `robust` is defined as "REx wins at EVERY supplied threshold" — with one
threshold it's just "REx wins," which is still a true (if weaker) statement. Document
that `robust` is meaningful only for >=2 thresholds. → documented in 09.

## Final filtered spec changes
- Add a load-time shape assert on `per_incident` (defensive, cheap).
- Document `best_control` tie-break ("first arm at max pass-rate") and that the GAP
  value is invariant to ties.
- Carry two honest caveats into 09: (a) clustered sample (eff. n < 15) → CI
  optimistic; (b) `robust` flag needs >=2 thresholds to mean anything.
No change to the core sweep math.
