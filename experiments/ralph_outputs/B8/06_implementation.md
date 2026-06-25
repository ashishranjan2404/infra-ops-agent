# 06 — Implementation

## Artifacts created (all under experiments/ralph_outputs/B8/artifacts/ — no shared-core edits)
- `effect_size.py` — library + CLI.
  - `cohens_h(p1,p2)` arcsine-transformed proportion gap, signed, validated `[0,1]`.
  - `pooled_sd(s1,n1,s2,n2)` weighted by (n-1), guards n.
  - `cohens_d(m1,s1,n1,m2,s2,n2)` pooled-SD standardized mean diff; sp==0 → inf/0.0.
  - `magnitude(es)` Cohen labels (negligible/small/medium/large).
  - `effect_sizes_for_file(data, baseline)` ingests `by_condition[c].overall`
    (`n, passes, mean_reward, reward_std`); recomputes `pass@1 = passes/n`; emits per-lift
    proportion (h) + continuous (d) effect sizes with magnitudes.
  - CLI: positional files, `--baseline`, `--json`, `--selftest`.
- `test_effect_size.py` — 10 pytest cases against hand-computed Cohen's d/h values + a
  synthetic end-to-end `effect_sizes_for_file` check.
- `effect_size_report.json` — computed effect sizes on the two real result files.

## Ouroboros fixes that landed in code
- div-by-zero guard in `cohens_d`; `[0,1]` validation in `cohens_h`; `passes/n` recompute;
  `KeyError` naming available conditions when `--baseline` is absent; non-finite-d safe
  pretty-printer.

## What it ran on (REAL inputs)
- `A1/artifacts/full_pass_at_k_glm-5p2.json` — 42 incidents × 3 seeds, n=126/condition.
- `A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json` — 30 incidents × 5 seeds, n=150/condition.

## Headline computed numbers (baseline = zero_shot)
**glm-5p2:** REx pass@1 0.230→0.897 → **Cohen's h = +1.49 (large)**; mean reward
0.429→0.943 → **Cohen's d = +1.73 (large)**. best_of_n / retry_realistic / rex_no_oracle:
h small (~0.23–0.26), d medium (~0.64–0.67).
**deepseek-v4-pro:** REx pass@1 0.240→0.893 → **h = +1.45 (large)**; reward
0.478→0.928 → **d = +1.46 (large)**. The three non-REx conditions: h **negligible**
(0.11–0.16), d **small** (0.32–0.39).

Key finding: only the REx lift is a *large* effect on both measures and both models; the
best-of-n / retry / no-oracle "lifts" are small-to-negligible once standardized — i.e. the
raw +0.11..+0.14 reward deltas they show are not impressive relative to baseline spread.

## No core files touched
`git status --porcelain experiments/ralph_outputs/B8` shows only new files under B8/.
