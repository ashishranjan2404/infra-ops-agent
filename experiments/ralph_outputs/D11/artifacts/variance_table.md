# Training Stability / Seed-Variance Report

- generated: `2026-06-25T08:03:49+00:00`
- mode: **cross-config**   last_k=5   collapse_thresh=0.03
- **seed_variance_status:** NOT MEASURED — trainer (train_rft.py / train_rft_v2.py) lacks a --seed flag; no run log contains a seed field. See add_seed_patch.diff + run_multiseed.sh (blocked on HUD Tinker GPU backend).

## Per-run stats
| run | steps | group_n | plateau_mean | **plateau_std** (stability) | within-step spread (mean/min) | curve_std (incl. trend — NOT stability) | delta (last-first) | collapse steps |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| `train_qwen3-8b.jsonl` | 25 | 24 | 0.4937 | 0.0209 | 0.1724/0.155 | 0.0223 | -0.031 | 0 |
| `train_qwen3-8b_v2.jsonl` | 15 | 40 | 0.5356 | 0.0071 | 0.183/0.1714 | 0.0136 | 0.0371 | 0 |
| `train_qwen3-30b.jsonl` | 14 | 24 | 0.4853 | 0.0302 | 0.1683/0.1555 | 0.0241 | 0.0168 | 0 |

## Cross-config spread (CAVEATED — NOT seed variance)
- plateau_means = [0.4937, 0.5356, 0.4853]
- min=0.4853  max=0.5356  std(ddof=1)=0.0269
- caveat: NOT seed variance. Confounds: (1) model size (8B vs 30B), (2) rollouts/step n (24 vs 40), (3) trainer version (v1 vs v2). No CI computed — these are different configs, not seeds of one config.

## Notes
- To get a real seed-variance CI: apply add_seed_patch.diff, run run_multiseed.sh (5 seeds, same config), then re-run with --seed-group.
- No within-step spread collapse (all steps >= 0.03); GRPO advantage signal preserved throughout every run.
