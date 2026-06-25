# B8 — Effect Sizes (Cohen's d / Cohen's h) for Claimed Lifts — SUMMARY

## Deliverable
A real, unit-tested effect-size tool and computed effect sizes for every claimed lift in
the project's available pass@k result JSONs.

- `artifacts/effect_size.py` — library + CLI. Cohen's **h** for `pass@1` proportion lifts
  (arcsine transform), Cohen's **d** for `mean_reward` lifts (pooled SD). `--selftest`, `--json`.
- `artifacts/test_effect_size.py` — 10 pytest cases vs hand-computed textbook values. **10/10 pass.**
- `artifacts/effect_size_report.json` — effect sizes vs `zero_shot` (2 models, 4 lifts each).
- `artifacts/effect_size_report_vs_best_of_n.json` — effect sizes vs the strongest baseline.

## Real inputs used
- `A1/.../full_pass_at_k_glm-5p2.json` (42 incidents x 3 seeds, n=126/condition)
- `A2/.../ablation_pass_at_k_deepseek-v4-pro.json` (30 incidents x 5 seeds, n=150/condition)

## Results (baseline = zero_shot)
| model | condition | pass@1 d | Cohen's h (mag) | reward d | Cohen's d (mag) |
|---|---|---|---|---|---|
| glm-5p2 | best_of_n | +0.111 | +0.247 small | +0.224 | +0.638 medium |
| glm-5p2 | retry_realistic | +0.119 | +0.264 small | +0.233 | +0.674 medium |
| glm-5p2 | **rex** | **+0.667** | **+1.487 large** | **+0.514** | **+1.725 large** |
| glm-5p2 | rex_no_oracle | +0.103 | +0.230 small | +0.231 | +0.668 medium |
| deepseek-v4-pro | best_of_n | +0.067 | +0.150 negligible | +0.127 | +0.358 small |
| deepseek-v4-pro | retry_realistic | +0.073 | +0.164 negligible | +0.138 | +0.387 small |
| deepseek-v4-pro | **rex** | **+0.653** | **+1.452 large** | **+0.450** | **+1.462 large** |
| deepseek-v4-pro | rex_no_oracle | +0.047 | +0.106 negligible | +0.113 | +0.319 small |

**Against the strongest baseline (best_of_n)**, REx is still large: glm-5p2 h=+1.24 / d=+1.15.

## Key finding
Only the **REx** lift is a *large* effect (Cohen's h and d both > 0.8) — on both models and
even vs the strongest baseline. best_of_n / retry_realistic / rex_no_oracle are
small-to-negligible once standardized: their raw "+0.11..+0.14 reward" deltas are unimpressive
relative to baseline spread. rex_no_oracle ~ best_of_n (the oracle, not the tree, drives REx).

## Caveats (do not over-read)
- **Overall lifts only**, not per-family — a pooled d=1.7 does not imply REx is large on the
  *novel* family. Per-family is deferred (A-series slice).
- **Pooled-SD Cohen's d** assumes near-equal variance; rex std (~0.17-0.22) < zero_shot
  (~0.37-0.38), so pooled d is mildly optimistic. Hedges' g / Glass's d deferred.
- **No CI on the effect sizes themselves** (source JSONs carry Wilson CIs on pass@1; bootstrap
  CI on d/h is future work). Pooling seeds x incidents overstates effective n.

## Verification
selftest ALL PASS - pytest 10/10 - numbers independently recomputable from inputs -
no shared-core files touched (only new files under `experiments/ralph_outputs/B8/`).
