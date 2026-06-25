# D11 — Summary: Training stability / variance across random seeds

## Task
Measure training stability (variance across random seeds) for the opensre RFT (GRPO) run.

## Key finding
The RFT trainers (opensre-traj/train_rft.py, train_rft_v2.py) expose NO `--seed` flag and
NO run log carries a seed field — so true multi-seed variance is NOT MEASURED and cannot be,
by construction, without GPU re-runs. This reproducibility gap is the headline result.

## Deliverables (all real, validated; no shared-core edits)
- artifacts/seed_variance.py — stdlib variance analyzer (per-run curve stats, detrended
  last-k plateau std, within-step reward spread, GRPO advantage-collapse flags, Student-t
  95% across-seed CI via --seed-group).
- artifacts/add_seed_patch.diff — VALID diff adding --seed to train_rft_v2.py (verified
  `git apply --check` -> clean); NOT applied to the shared file.
- artifacts/run_multiseed.sh — 5-seed launch driver (blocked on HUD GPU backend).
- artifacts/test_seed_variance.py — 10 pytest cases, all pass.
- artifacts/variance_report.json + variance_table.md — generated from the 3 REAL logs.

## Real variance numbers (from actual run logs)
| run | steps | n | plateau_mean | plateau_std (stability) | within-step spread |
|---|--:|--:|--:|--:|--:|
| qwen3-8b     | 25 | 24 | 0.4937 | 0.0209 | 0.172 |
| qwen3-8b_v2  | 15 | 40 | 0.5356 | 0.0071 | 0.183 |
| qwen3-30b    | 14 | 24 | 0.4853 | 0.0302 | 0.168 |

- Cross-config plateau-mean std(ddof=1) = 0.0269 (CAVEATED — confounded by model size / n /
  trainer version; NOT seed variance).
- No within-step spread collapse in any run -> GRPO advantage signal preserved.
- Most stable plateau: the v2 run (plateau std 0.0071).

## Status
completed — real plan + spec + runnable validated artifacts + real observable-variance
numbers delivered; the across-seed CI itself is the one documented blocker (no seed knob +
GPU re-runs required).
