# D11 — Implementation

## Artifacts built (all under experiments/ralph_outputs/D11/artifacts/, no shared edits)

1. **`seed_variance.py`** (11 KB, stdlib-only, executable) — the variance analyzer.
   - `load_run` (robust jsonl parse, skips blank/malformed lines),
   - `per_step_spread` (uses logged `reward_std`, else recomputes population std),
   - `run_stats` (curve_mean, curve_std, last-k **plateau_std** = detrended stability,
     within-step spread mean/min, GRPO collapse-step flags, delta),
   - `seed_ci` (Student-t 95% CI across seeds; needs S>=2),
   - `t_multiplier` (hardcoded 95% t-table df 1..30, else 1.96),
   - `build_report` / `render_md` (JSON + markdown; top-level `seed_variance_status`).
   - Two modes: cross-config (default) and `--seed-group` (real seed CI).

2. **`add_seed_patch.diff`** — a VALID unified diff adding `--seed` to
   `opensre-traj/train_rft_v2.py` (seeds `random`, numpy, exports PYTHONHASHSEED /
   HUD_ROLLOUT_SEED). **Verified with `git apply --check` → applies cleanly.**
   NOT applied to the shared core file (brief rule); delivered as a documented patch.

3. **`run_multiseed.sh`** — driver that launches the same config under seeds {0,1,2,3,4}
   into `runs/seeds/seed_<s>.jsonl`, then prints the exact `seed_variance.py --seed-group`
   command to analyze them. `bash -n` clean. Blocked on HUD GPU backend (documented).

4. **`test_seed_variance.py`** — 10 pytest cases (spread source, plateau clamp, collapse
   flag, known-value CI, single-seed None, large-df t, report status). All pass.

5. **Generated REAL outputs:** `variance_report.json` + `variance_table.md`, produced by
   running the analyzer on the 3 actual run logs in `opensre-traj/runs/`.

## Real numbers (from the 3 actual opensre RFT logs)
| run | steps | n/step | plateau_mean | plateau_std (stability) | within-step spread | curve_std |
|---|--:|--:|--:|--:|--:|--:|
| train_qwen3-8b      | 25 | 24 | 0.4937 | **0.0209** | 0.1724 | 0.0223 |
| train_qwen3-8b_v2   | 15 | 40 | 0.5356 | **0.0071** | 0.1830 | 0.0136 |
| train_qwen3-30b     | 14 | 24 | 0.4853 | **0.0302** | 0.1683 | 0.0241 |

- Cross-config spread of plateau means: min 0.4853, max 0.5356, std(ddof=1) **0.0269**
  — labelled NOT seed variance (3 stacked confounds).
- No within-step spread collapse in any run (all steps >= 0.03) → GRPO advantage signal
  preserved; the v2 run has the lowest plateau std (0.0071 → most stable plateau).

## Why no real seed-variance CI
`train_rft.py` and `train_rft_v2.py` expose no `--seed`; no log has a seed field. A real
across-seed CI requires the patch + 5 GPU re-runs (blocked). The CI code path is exercised
by `test_seed_variance.py` on synthetic fixtures only — never written into the real report.
