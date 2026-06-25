# D1 — 01 Plan

## Objective
Run the opensre RFT/GRPO training run for **50+ steps** (current runs are only
15–25 steps) to test whether the observed **+0.037 mean-reward trend** continues
or plateaus. The trend comes from `opensre-traj/runs/train_qwen3-8b_v2.jsonl`:
mean_reward 0.5039 (step 0) → 0.5410 (step 14), Δ = +0.0371 over 15 steps.

## Grounding (existing assets, unmodified)
- `opensre-traj/train_rft_v2.py` — the v2 GRPO launcher (P0 deterministic
  mechanism reward via `hud_env_v2.py`, 10 tasks, per-step reward-spread logging,
  transient-5xx retry wrapper). This is the canonical launcher.
- `opensre-traj/train_rft.py` — v1 launcher (4 tasks, coarser reward).
- `opensre-traj/runs/train_qwen3-8b_v2.jsonl` (15 steps) and
  `train_qwen3-8b.jsonl` (25 steps) — the existing partial curves.
- Forked trainable model slug: `opensre-qwen3-8b-1e439a` (Qwen3-8B via Tinker).
- `.venv-hud/bin/python` (HUD SDK) — training is the HUD Python SDK, not a CLI.

## Approach
1. Confirm the +0.037 trend numerically (delta + OLS slope) from the existing v2 JSONL.
2. Build a **50-step launcher** (`run_rft_50.sh`) that wraps `train_rft_v2.py`
   with `--steps 50` and the *same* hyper-params (group 6, lr 1e-5, tasks 0–9)
   so the new curve is directly comparable to the 15-step one.
3. Build a stdlib **curve analyzer** (`analyze_curve.py`) that reports
   delta / OLS slope / horizon projection / verdict (continuing / flat / reversed)
   for any run JSONL — the tool that actually answers "does the trend continue?".
4. Prove the pipeline against the live HUD/Tinker backend with a 1-step smoke.
5. Within the ~15-min compute cap, launch the real 50-step run in the background
   and capture whatever partial curve completes; document the compute blocker if
   it cannot finish 50 steps in time. **Never fabricate steps.**

## Files to create (all task-namespaced)
- `experiments/ralph_outputs/D1/artifacts/run_rft_50.sh` — launcher (no core edits).
- `experiments/ralph_outputs/D1/artifacts/analyze_curve.py` — analyzer.
- `experiments/ralph_outputs/D1/artifacts/train_d1_50step.jsonl` / `.log` — real partial curve.

## Dependencies / risks
- **Compute**: real GRPO needs the Tinker GPU backend; ~30–90 s/step. 50 steps can
  take 30–90 min → cannot complete within a 15-min cap. Mitigation: deliver the
  runnable launcher + a real partial curve + a documented blocker.
- **Transient 5xx** from the Tinker forward/backward endpoint (killed a prior 30B
  run at step 13). Mitigated by the retry wrapper already in `train_rft_v2.py`.
- **Headroom risk**: tasks 0–9 start near the model ceiling (~0.5), so the slope is
  small and may be within-noise. Honest reporting required.

## Success criteria
- Runnable, syntax-valid 50-step launcher that reuses the unmodified v2 trainer.
- A working analyzer that quantifies the trend and projects to a 50-step horizon.
- Live-backend smoke proving rollout → reward → forward/backward works.
- A real (possibly partial) 50-step curve OR a clearly documented compute blocker.
- No edits to any shared core file.
