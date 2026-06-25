# A7 — 05 Ouroboros (3 self-critiques in sequence)

## Engineer A — correctness & edge cases
- **Problem:** `max((g.get("buried_under",0) ...) for g in guns)` raises on an
  empty `guns` list. → **Fixed:** guarded with `if guns else 0`.
- **Problem:** `severity` / `flap_prob` could be `None` if a YAML omits them;
  `float(None)` throws. → **Fixed:** all `.get(...)` calls carry numeric
  defaults and are wrapped in `float(... or 0)` where the value feeds `float`.
- **Problem:** A scenario with 1 node and 0 edges must not produce a negative
  topology term. `(1-1)/6 = 0` and `clamp` floors it — OK.

## Engineer B — over/under-engineering & discrimination power
- **Problem:** severity is **always 0.7** across the corpus and flap_prob always
  0.05 — these terms add a constant offset and zero discrimination. Keeping them
  is mild over-engineering. → **Decision:** keep but down-weight (0.06 / 0.05
  caps). They cost nothing and make the score robust if future scenarios *do*
  vary severity/flap. Documented as low-variance in 09.
- **Problem:** Is a 10-term trap score over-built for a corpus that's mostly two
  clusters (synthetic-easy vs postmortem-hard)? → **Decision:** the extra terms
  give within-cluster ordering (e.g. 4-node vs 5-node postmortems separate),
  which curriculum sampling wants. Justified.

## Engineer C — semantics, naming, calibration
- **Problem:** `expected_pass_rate` implies an empirical rate; it's a prior.
  → **Resolution:** can't rename (task contract); JSON `schema` block states it
  is a prior; 09 carries the uncalibrated caveat. Carried from grill.
- **Problem:** thresholds 0.70/0.45 are arbitrary. With base 0.92 and trap cap
  0.55, the *floor* of epr is ~0.37, so "hard<0.45" is reachable and "easy≥0.70"
  requires tc≲0.4 — i.e. buckets are actually attainable across the realised
  range (verified empirically: 8/16/9 split). → **Accepted** as reasonable;
  noted thresholds are tunable knobs, not laws.
- **Problem:** sort puts hardest first which could confuse a reader expecting
  easy-first. → **Resolution:** schema documents bucket rule; CSV is sortable
  by the consumer. Minor, left as-is.

## Final filtered spec
No structural change from 04; the empty-`guns` guard and `None`-safe numeric
coercion are the concrete code fixes that made it into the implementation. All
three semantic concerns are resolved by documentation rather than code, and are
recorded as honest limitations in 09.
