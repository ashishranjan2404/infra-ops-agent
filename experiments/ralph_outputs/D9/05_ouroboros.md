# D9 — 05 Ouroboros (self-critique, 3 engineers in sequence)

## Engineer A — "the simulation is doing the work the model should do"
**Problem:** The headline result (curriculum > random) is BAKED IN by the
Gaussian band model — any monotone-difficulty schedule that keeps incidents near
a rising competence will beat a shuffle. This is tautological if presented as
evidence that curriculum *works on the actual model*.
**Fix:** Reframe explicitly: the harness demonstrates a *mechanism* and provides
falsifiable, reusable infra — it is NOT evidence about the real policy. Loud
`kind`/`model_note` labels + the blocker section in 07/09 must say this in plain
language. Keep the sim because it (a) validates the schedule plumbing end-to-end
and (b) gives the real run a hypothesis to confirm/refute. Accepted.

## Engineer B — "band edges and forgetting are under-modeled"
**Problem 1:** `_bands` splits the *ordered* list, but for `random`/`anti` the
"newly_unlocked" bands are not difficulty-contiguous, so the RLE within-group-
spread guarantee only holds for curriculum. **Fix:** Documented — that asymmetry
is the *point* of the control (random deliberately destroys difficulty structure);
spread preservation is a curriculum property we *claim*, not a control property.
**Problem 2:** Rehearsal is modeled as continued sampling but the sim has NO
forgetting term, so rehearsal never matters numerically here. **Fix:** Concede —
rehearsal weight flows into the *schedule/config* (where a real trainer uses it)
but the simulation, lacking a decay term, can't show its benefit. Noted as a sim
limitation in 09; not worth adding a fake forgetting term.

## Engineer C — "absolute reward numbers look broken / mean difficulty mismatch"
**Problem:** Final mean_reward tops out ~0.20 even for curriculum, which looks
like a bug. Cause: mean incident difficulty ≈12.4 but competence only climbs to
~5 over 5–6 stages, so most hard cascades stay "unsolved" in the proxy.
**Fix:** This is *intended* and realistic (hard real-outage cascades are rarely
one-shot solved), and the **relative** ordering is the scientific claim, not the
absolute floor. Document the absolute-floor caveat so a reviewer doesn't read it
as a failure. Confirmed not a bug: sigmoid(K*(c-d)) with c<<d → ~0, correct.
**Also:** assert rewards ∈ [0,1] (test 8) guards against a real sigmoid bug.

## Final filtered spec deltas
- Add explicit "this is a mechanism demo, not model evidence" framing to harness
  output + 07/09. (A)
- Document: spread-preservation is a curriculum claim; random control intentionally
  breaks it. (B1)
- Document: sim has no forgetting term → rehearsal benefit lives in config, not
  the sim curve. (B2)
- Document: low absolute rewards are expected (high mean difficulty); relative
  AUC delta is the result. (C)
No code redesign needed; all four are framing/limitation notes + the existing
unit-interval assertion.
