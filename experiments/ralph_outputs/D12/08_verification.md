# D12 — 08 Verification

## Success criteria (from 01) vs reality
| criterion | met? | evidence |
|-----------|------|----------|
| group=8 config parses | YES | T1 PASS, `group==8` |
| launcher valid | YES | T2 `bash -n` PASS, `chmod +x` |
| analysis runs on REAL log, prints sigma + SEM(4) vs SEM(8) | YES | T3, sigma=0.0689 from `train_qwen3-8b_v2.jsonl` |
| 29.3% / 50% reduction figures derived (not asserted) | YES | computed in-script |
| honest verdict + blocker documented | YES | `07`, `09` |
| group=8 actually exercised | YES (bonus) | live smoke `n=16 = 2×8`, "SMOKE OK" |

## Are outputs real, not placeholder?
- `variance_analysis.py` reads a real 15-step training log and recomputes sigma each run —
  no hardcoded numbers in the output.
- `group8_smoke.log` is captured live HUD harness output (real job id, real rewards).
- The 29.3% / 50% figures are mathematical identities (1−1/√2, 1−1/2) confirmed numerically
  against the empirical sigma, not invented.

## Does "more rollouts help?" — verdict
- **Statistically: yes, modestly.** Group 4→8 cuts the GRPO baseline-mean standard error by 29.3%
  (variance −50%), giving a cleaner advantage estimate per step.
- **For THIS run's flat reward: not the fix.** The baseline-mean SEM was already small (~0.034)
  relative to within-group sigma (~0.069); the diagnosed flat-reward cause was too few tasks +
  low learnable headroom, which more rollouts do not address. 4→8 is a second-order win at 2×
  rollout cost — worth it only after the task-set / headroom fixes from v2 are in place.

Verification status: **PASS** (deliverable complete; full training run blocked by compute cap +
unforked slug, both documented).
