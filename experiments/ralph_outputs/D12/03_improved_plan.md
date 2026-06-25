# D12 — 03 Improved Plan

## What changed after the grill
1. **Baseline is the logged group=4**, not the v2 CLI default of 6 (RLE). The analysis and config
   both treat 4→8 as the comparison.
2. **Derive sigma from the real log** rather than asserting it (SMR + AAAI). `variance_analysis.py`
   reads `train_qwen3-8b_v2.jsonl` and computes per-task within-group sigma (≈0.069).
3. **Two A/B framings documented** (AAAI): fixed-steps (group8 pays 2×/step) vs matched-compute
   (group8@N steps vs group4@2N steps). Config defaults to fixed-steps; note explains the trade.
4. **Honesty clause** (PSRE): the deliverable explicitly states 4→8 reduces baseline-mean error
   (29.3%) but is a *second-order* fix that does NOT cure the diagnosed flat-reward root cause.
5. **Blocker stated up front** (DVO): 80 rollouts/step × 30 steps is infeasible under a 15-min cap
   with one slug; deliver config + smoke path + projection.

## Critiques accepted
- AAAI's two-framings point → added to config comments + analysis output.
- RLE's "use logged 4" → baseline constant `BASE_G=4` in the script.
- PSRE's "don't oversell" → explicit interpretation paragraph in the script output.

## Critiques rejected (with reason)
- AAAI's full seed-sweep requirement → **rejected for this deliverable**: one forked slug + 15-min
  cap makes it impossible; we label results a *projection*, which is the honest alternative.
- PSRE's "it mostly burns compute" → **softened, not adopted**: RLE's counter (noisy baseline
  injects gradient variance that can stall real learning) means 4→8 is a genuine if modest win,
  so we present it as second-order-positive, not worthless.

## Final plan
Unchanged file set (`group8_config.yaml`, `run_group8.sh`, `variance_analysis.py`), now grounded in
the real log with both A/B framings and an explicit honesty clause + documented compute blocker.
