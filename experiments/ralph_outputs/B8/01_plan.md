# 01 — Plan (Task B8: Effect sizes for claimed lifts)

## Objective
Every headline in this project is a *lift* — "REx lifts pass@1 from 0.23 to 0.90",
"+0.45 mean reward". A raw delta is not a defensible claim: a +0.1 jump off a 0.05
baseline and a +0.1 jump off a 0.45 baseline are statistically different animals.
B8 computes **standardized effect sizes** (Cohen's d / Cohen's h) for all claimed
lifts in the available pass@k result JSONs, so reviewers can see whether the lift is
"large" or "negligible" in Cohen's terms.

## Approach
- **Cohen's h** for the binary `pass@1` proportion lifts (arcsine-transformed gap;
  the correct measure for two probabilities, robust near 0/1).
- **Cohen's d** for the continuous `mean_reward` lifts (pooled-SD standardized).
- Ingest the real result files (output shape of `rex/eval_pass_at_k.py`:
  `by_condition[cond].overall` with `n, passes, mean_reward, reward_std`).
- Report every non-baseline condition's lift vs the `zero_shot` baseline.

## Files to create (all task-namespaced, NO shared-core edits)
- `artifacts/effect_size.py` — library + CLI (`cohens_d`, `cohens_h`, `pooled_sd`,
  `magnitude`, `effect_sizes_for_file`, `--selftest`, `--json`).
- `artifacts/test_effect_size.py` — pytest with known textbook values.
- `artifacts/effect_size_report.json` — computed effect sizes on real data.

## Inputs available (real)
- `experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json` (42 incidents, 3 seeds, n=126/cond)
- `experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json` (30 incidents, 5 seeds, n=150/cond)
- Also `rex/runs/frontier.json` / `ablation.json` (read-only, for context; lack per-cell n).

## Dependencies
Python 3.13 stdlib only (`math`, `json`, `argparse`). pytest for tests. No network, no GPU.

## Risks
- Mis-pairing the SD: `reward_std` is the within-condition spread; must use *pooled* SD.
- `pass@1` is a proportion → must use h, NOT d (d on a 0/1 variable is degenerate).
- Degenerate pooled SD = 0 → guard against div-by-zero.

## Success criteria
1. `--selftest` and pytest pass against hand-computed Cohen's d/h values.
2. Real effect sizes produced for every claimed lift, per model, with magnitude labels.
3. No shared core file touched.
