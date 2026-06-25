# 08 — Verification

## Against success criteria (from 01/03)
1. **Self-test + pytest pass against hand-computed Cohen's d/h** — YES.
   10/10 pytest, 9/9 selftest assertions. Values verified by hand: `cohens_h(0.5,0.25)=pi/6`,
   `cohens_h(1,0)=pi`, `cohens_d(7,2,2,5,2,2)=1.0`, `pooled_sd(3,5,5,5)=sqrt(17)`.
2. **Real effect sizes for every claimed lift, per model, with magnitudes** — YES.
   8 lifts total (4 conditions × 2 models) vs zero_shot baseline, both h (proportion) and
   d (continuous), each labeled. Persisted to `effect_size_report.json`.
3. **No shared-core file touched** — YES. `git status --porcelain experiments/ralph_outputs/B8`
   shows only the new `B8/` tree (`??`). No `rex/*.py`, `sim/*.py`, `agent/*.py`,
   `experiments/*.py`, status/dashboard changes.

## Outputs are REAL, not placeholder
- Numbers are derived from the actual A1/A2 result JSONs (n=126 and n=150 per condition,
  real `passes`, `mean_reward`, `reward_std` values), not invented.
- The math is independently checkable: e.g. glm-5p2 REx h —
  `2*asin(sqrt(0.8968)) - 2*asin(sqrt(0.2302)) = 2.4972 - 1.0099 = 1.487`. Matches output.
- Report regenerates deterministically from the same inputs (stdlib, no RNG, no network).

## Cross-check on the two flagship REx lifts
| model | pass@1 base→treat | h (mag) | reward base→treat | d (mag) |
|---|---|---|---|---|
| glm-5p2 | 0.230→0.897 | +1.49 large | 0.429→0.943 | +1.73 large |
| deepseek-v4-pro | 0.240→0.893 | +1.45 large | 0.478→0.928 | +1.46 large |

Both REx lifts are unambiguously *large* on both measures. Verified.
