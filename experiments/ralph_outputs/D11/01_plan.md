# D11 — Training Stability: Variance Across Random Seeds (Plan)

## Objective
Quantify the **training stability** of the opensre RFT (GRPO) run by measuring the
**variance of the learning curve across random seeds**, and report a confidence
interval (CI) on the key training metric (mean per-step reward / final reward).

## Grounding (real files)
- `opensre-traj/train_rft.py` — the RFT/GRPO trainer (HUD Tinker provider, Qwen open models).
- `opensre-traj/train_rft_v2.py` — v2 trainer (10 tasks, logs `reward_std` per step).
- Run logs that actually exist:
  - `opensre-traj/runs/train_qwen3-8b.jsonl`   (25 steps, group=24, n=24/step)
  - `opensre-traj/runs/train_qwen3-8b_v2.jsonl` (15 steps, n=40/step, has `reward_std`)
  - `opensre-traj/runs/train_qwen3-30b.jsonl`  (14 steps, n=24/step)

## Critical finding (drives the plan)
Neither `train_rft.py` nor `train_rft_v2.py` exposes a `--seed` flag, and no log
contains a `seed` field. **There are no real multi-seed training logs** — every
existing run is a single (model, config) trajectory, not N seeds of the same config.
GRPO re-runs require the HUD Tinker GPU backend + `HUD_API_KEY` + paid forward/backward
steps, which is not runnable inside this worker.

So the task splits into:
1. **Deliverable A (runnable harness):** a `--seed` patch for the trainer + a
   multi-seed driver + a variance-analysis script. These are REAL and runnable
   (the analysis script runs now on real data; the GPU re-run is the documented blocker).
2. **Deliverable B (real numbers now):** extract the *observable* variance that the
   existing logs DO contain and report it honestly:
   - **Within-step reward spread** (std of the `rewards[]` array each step) — the GRPO
     advantage-normalization signal; this is genuine stochasticity already logged.
   - **Step-to-step curve variance** of `mean_reward` (a stability proxy for a single seed).
   - **Cross-config variance** (8b vs 8b_v2 vs 30b) as a coarse, caveated stand-in for
     seed variance, clearly labelled as confounded (different model/n), NOT seed variance.

## Approach
- `seed_variance.py` (artifacts): pure-stdlib analyzer. Inputs: one or more run jsonl logs.
  Computes per-run curve stats (mean, std, last-k mean), within-step spread, and — when
  given ≥2 logs of the SAME config tagged as seeds — a proper across-seed mean ± 95% CI
  on final reward and on the whole curve. Emits a JSON report + a markdown table.
- `add_seed_patch.diff` (artifacts): a `.patch` adding `--seed` to `train_rft_v2.py`
  (seeds python `random`, numpy, and passes `seed` into the HUD Job/rollout) — documented,
  NOT applied to the shared core file.
- `run_multiseed.sh` (artifacts): driver that would launch the same config under seeds
  {0,1,2,3,4} into `runs/seed_<s>.jsonl` (blocked on GPU, but real and correct).
- Run `seed_variance.py` on the 3 real logs now → real report.json + table.

## Files to create (all task-namespaced, no shared edits)
- `experiments/ralph_outputs/D11/artifacts/seed_variance.py`
- `experiments/ralph_outputs/D11/artifacts/add_seed_patch.diff`
- `experiments/ralph_outputs/D11/artifacts/run_multiseed.sh`
- `experiments/ralph_outputs/D11/artifacts/test_seed_variance.py`
- `experiments/ralph_outputs/D11/artifacts/variance_report.json` (generated)
- `experiments/ralph_outputs/D11/artifacts/variance_table.md` (generated)
- 10 step files + SUMMARY.md + result.json

## Dependencies
- Python 3.13 stdlib only (json, statistics, math, argparse, glob). No numpy required for
  the analyzer (keeps it runnable here). The seed patch references numpy only inside the
  trainer (already in the HUD venv).

## Risks
- Cross-config variance is NOT seed variance — must be labelled to avoid a reviewer
  conflating them. Mitigated by separate report sections + explicit caveats.
- Small step counts (14–25) → wide CIs. Report honestly with n and t-multiplier.
- Statistical CI on a single seed's curve is autocorrelated (steps not iid) — flag it.

## Success criteria
- `seed_variance.py` runs on the 3 real logs and emits a valid JSON + md table with
  real numbers (mean reward, within-step spread, curve std, CI where ≥2 seeds).
- The `--seed` patch parses as a valid diff and is logically correct.
- `test_seed_variance.py` passes under pytest.
- Blocker (no real multi-seed GPU runs) documented honestly; no fabricated seed numbers.
