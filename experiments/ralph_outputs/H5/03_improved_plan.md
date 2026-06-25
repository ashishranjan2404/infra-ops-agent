# H5 — 03 Improved Plan

## What changed after the grill
1. **Three-test gate (AND).** Adopted SMR + PSRE + RLE: PROMOTE requires absolute
   `pass@1 >= 0.80` AND `CI_lo >= 0.70` AND `lift_over_baseline >= 0.20`. Fail lift →
   REJECT; otherwise HOLD. This replaces my original single pass@1 threshold.
2. **CI_lo is a hard requirement, not a tiebreaker.** Accepted SMR over PSRE: with wide
   CIs you should NOT auto-promote; that is exactly when promotion is risky.
3. **Anti-selection-bias.** Accepted SMR/REV: the manifest carries ALL five conditions
   per model (zero_shot, best_of_n, retry_realistic, rex, rex_no_oracle), so the gate is
   tested against losers too — not a cherry-picked winners list.
4. **Lift is per-model, vs the model's own zero_shot.** Accepted PSRE so a high task-floor
   model can't masquerade as a good method.
5. **Loud fetch failure + file-picker fallback.** Accepted DOL/REV: fetch the live
   manifest (don't embed), but on failure show an explicit message with a
   `python3 -m http.server` hint and a file picker.

## Critiques rejected (and why)
- **DOL: "embed the data into the HTML."** Rejected (per REV) — embedding freezes the
  manifest and kills the live-monitoring premise. Fallback file-picker is the right
  compromise.
- **PSRE: "drop absolute pass@1, gate on lift only."** Rejected (per RLE) — lift alone is
  gameable by a bad baseline. Kept both tests.

## Final shape
- `gen_manifest.py` → normalizes A1 + A2 into `sre-degrees.promotion-manifest/v1`, all
  conditions, with provenance block.
- `dashboard.html` → counters, per-model table (pass@1 bar + CI band + threshold tick,
  pass@2/5, lift, per-family pass@1, gate tag with reasons), sortable, file-picker fallback.
- Verify: JSON valid, HTML parses, served over HTTP 200, JS renders correct gate counts.
