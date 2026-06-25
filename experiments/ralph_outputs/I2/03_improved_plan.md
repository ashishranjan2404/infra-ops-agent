# I2 — 03 Improved Plan

## What changed after the grill
1. **Condition the bimodality claim** on the competent / resolved-eligible
   subpopulation (diag=fix=resolved=1; only `trap` varies). This is the clean
   two-atom law. (Accepted REV's "the full population is multi-modal" critique.)
2. **Primary metric = valley test** (largest-gap with mass on both sides), BC as
   secondary illustration only — do NOT gate the conclusion on BC. (Accepted RLE.)
3. **Two distinct, both-true facts** are reported separately and honestly:
   - (a) a *valley* appears once the atoms separate (around tp ≈ 0.2 with our gap
     threshold);
   - (b) the **resolved-reward-nullifying** threshold is *exactly* `tp > W_RESOLVED`
     — the economically meaningful one the task asks about.
   Avoids the misleading single "threshold confirmed" boolean. (Accepted SMR/REV.)
4. **Caveat documented**: for very large penalties the trap atom clamps to 0,
   erasing the *degree* of badness (gradient information loss). (Accepted SMR.)
5. **Reproducibility**: seeded RNG + assert mirrored constants == `rex/scoring.py`.
   (Accepted DEV.)

## Critiques accepted
- REV: full population is multi-modal — must condition. ✔
- SMR: pick the *minimal nullifying* threshold, not "as big as possible." ✔
- RLE: don't gate on BC; valley test is the honest one on discrete support. ✔
- DEV: seed + drift-guard. ✔

## Critiques rejected (with reason)
- PSRE "bimodality is purely a feature, no cost": rejected as the *framing* for
  this proof. It IS desirable operationally, but the task asks to *prove the
  distribution is bimodal*, which is a statement about the law, not a value
  judgment. We note the operational benefit but keep the proof neutral.
- RLE "reduce everything to optimizer variance": partially rejected — we mention
  the GRPO implication in the critique file, but the deliverable is the
  distributional proof, so we don't make the optimizer the centerpiece.

## Final deliverables (unchanged paths)
- `artifacts/bimodality_sim.py`, `artifacts/test_bimodality.py`,
  `artifacts/bimodality_result.json`.
