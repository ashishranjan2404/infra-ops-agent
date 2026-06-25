# I2 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — Distributional statistician (finds: definition gaps)
- **Problem 1**: "Bimodal" on a *discrete two-atom* support is technically a
  two-point distribution, not a continuous bimodal density. A purist will say
  "modes of a pmf vs density." → Fix: explicitly frame it as a two-atom mixture
  and use the valley/mass test, which is well-defined for both pmf and density.
- **Problem 2**: Sarle's BC reported as 0.32 (<0.555) would *contradict* a
  "bimodal" claim if read naively. → Fix: state in the spec that BC is unreliable
  on bounded discrete support and is reported for context only; the valley test
  governs. (Done — BC kept secondary, not a gate.)
- **Problem 3**: `largest_gap` on the FULL population picks a 0.125 gap and the
  default `is_bimodal` flips depending on `gap_thresh`. This is fragile. → Fix:
  the headline claim uses the *conditioned* subpopulation where the gap is 0.6
  (robust); the full-population number is descriptive only.

## Engineer B — RL practitioner (finds: realism / coupling gaps)
- **Problem 4**: The synthetic `draw()` coupling (resolved depends on fix and
  trap) is an assumption, not data. A reviewer asks "is bimodality an artifact of
  your coupling?" → Fix: the theorem does NOT depend on coupling — it conditions
  on `C` directly via `resolved_eligible_subpop`, which fixes diag=fix=resolved=1
  and varies only `trap`. Coupling only affects the (descriptive) full histogram.
- **Problem 5**: `p_trap` is a free knob; if 0 or 1 there is no bimodality
  (one atom). → Fix: stated as a precondition `0 < p_trap < 1` in the spec;
  default 0.35 is well inside.
- **Problem 6**: No connection to the *real* scorer — could be reimplementing it
  wrong. → Fix: `test_constants_match_source` imports `rex/scoring.py` and asserts
  equality; `score()` mirrors the exact clamp arithmetic and is unit-tested
  against hand-computed values.

## Engineer C — Skeptical reviewer (finds: over/under-claiming)
- **Problem 7**: Original code printed `THRESHOLD CONFIRMED: False`, which *looks
  like the proof failed*. Misleading. → Fix: replaced with two precise booleans —
  `valley_present_at_shipped_penalty` and `nullification_threshold_is_W_RESOLVED`
  — both True. No single ambiguous flag.
- **Problem 8**: The task says "trap penalty > resolved reward creates
  bimodality"; we must not overclaim that NO bimodality exists below the threshold
  (a smaller valley still exists for tp ≈ 0.2–0.4). → Fix: we explicitly separate
  "any valley" (appears earlier) from "nullifies resolved reward" (exactly
  `tp > W_RESOLVED`). Honest about both.
- **Problem 9**: Clamp at 0 means penalties ≥ MAX_CLEAN are indistinguishable. →
  Documented as a caveat (information loss), not hidden.

## Final filtered spec (deltas applied)
- Headline = conditioned two-atom law; full population labelled multi-modal.
- Valley test primary; BC secondary with stated unreliability.
- Two explicit truth booleans instead of one ambiguous flag.
- Precondition `0 < p_trap < 1` stated.
- Drift-guard test against `rex/scoring.py`.
- Clamp caveat documented.
