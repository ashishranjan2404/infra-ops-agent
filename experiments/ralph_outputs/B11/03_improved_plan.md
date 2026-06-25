# 03 — Improved plan (post-grill)

## What changed vs 01
1. **Reward is discrete-banded** (RLE): the weighted-sum reward lands on a small set
   of values, so thresholds in the same gap give identical pass-rates. The script
   must REPORT this rather than let the table look mysteriously flat. → 04 spec adds
   an observed-reward-bands section; 09 critique discusses it openly.
2. **Offline estimator equivalence check** (PSRE↔DEVOPS compromise): the copied
   `binary_pass` / `wilson_ci` must be verified against the canonical formula offline
   (no import of `rex.eval_pass_at_k`, which needs network/keys). → added to 07.
3. **Headline = the GAP, and its widening** (SMR): report `rex_minus_best_control` per
   threshold and feature that the gap widens from +0.20 (0.70) to +0.33 (>=0.80).
4. **Honesty on stats** (AAAI): emit Wilson 95% CIs; claim "rank-order/gap preserved,"
   never "significant at every cutoff." n=15/arm is stated as the limitation.

## Critiques accepted
- RLE discrete-band warning — accepted (report bands).
- PSRE/DEVOPS estimator-drift guard — accepted as an offline equivalence test.
- AAAI redundant-threshold optics — accepted: keep 0.86/0.90, justify each as a
  strict-end stress point in the spec.
- SMR gap-widening framing — accepted as the headline.

## Critiques rejected (with reason)
- AAAI "show a reward histogram" — REJECTED (RLE's argument): with 15 points and a
  reward that takes ~6 discrete values, a histogram is decoration; listing the bands
  is more honest and precise. Over-engineering avoided.
- PSRE "only the strict end (0.90) matters" — REJECTED (SMR's argument): the lenient
  end (0.70) is informative because it shows controls catching up; reporting both
  ends is what makes the widening-gap story credible.

## Final deliverable (unchanged shape)
- `artifacts/threshold_sweep.py` (standalone, no shared imports).
- `artifacts/robustness.json` (per-arm pass-rate + Wilson CI + gap, per threshold).
- Test: parse-check + estimator equivalence + verify gap monotonic/REx-wins.
