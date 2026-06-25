# B2 — Step 8: Verification

## Success criteria (from 01_plan.md) — checked

| Criterion | Status | Evidence |
|---|---|---|
| `mcnemar.py` ingests real pass@k JSON, emits full 10-pair table per family | MET | step 07 run; `mcnemar_pairwise_report.json` has 4 families x 10 pairs x 2 models |
| Standalone, dependency-free (no scipy) | MET | `import math, json, argparse, itertools` only; `python3 -m py_compile` OK |
| Exact binomial (not asymptotic chi-square as headline) | MET | `p_exact` via `math.comb`; chi2_cc secondary in JSON only |
| Multiple-comparison correction | MET | Holm-Bonferroni; `significant_holm` reported alongside raw |
| Reproduces A2's rex-vs-control discordant counts | MET | 4/4 exact match (step 07 #4) |
| Unit tests pass | MET | 11/11 (step 07 #2) |
| Real p-values reported, not placeholder | MET | concrete tables in step 07 + JSON artifact |

## Are the outputs real (not placeholder)?
Yes. Numbers are computed by the tool from the actual cached reward arrays in A1 and A2
artifacts (which themselves come from real eval runs: A1 n_jobs=630, A2 n_jobs=750,
n_errors=0). The cross-check that B2 independently reproduces A2's published discordant
counts is the strongest evidence the pipeline is doing real arithmetic on real data, not
emitting canned values.

## Headline real findings
- **REx is significant vs every control under Holm, for both models** (rex vs zero_shot /
  best_of_n / retry_realistic / rex_no_oracle: p_exact < 1e-6, p_holm < 1e-6). This is the
  paper's central claim, now actually backed by the paired test it claimed.
- The oracle ablation (**rex vs rex_no_oracle**) is also strongly significant — REx's gain
  is not just the oracle; removing it collapses performance (b01=71 glm / 91 deepseek, b10=0).
- Among the *weak* baselines, most pairwise differences (best_of_n vs retry_realistic vs
  rex_no_oracle) are **not** significant — honestly reported, they are statistically
  indistinguishable from each other.
- `best_of_n vs zero_shot` is significant for glm (p_holm 0.005) but **loses significance
  after Holm for deepseek** (p_exact 0.013 -> p_holm 0.065). A reviewer would have wrongly
  called this significant on raw p; B2 catches it. This is exactly the value the task adds.

## Reproduce
```
cd /Users/mei/rl
python3 experiments/ralph_outputs/B2/artifacts/test_mcnemar.py
python3 experiments/ralph_outputs/B2/artifacts/mcnemar.py \
  experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json \
  experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json \
  --out /tmp/check.json
```
