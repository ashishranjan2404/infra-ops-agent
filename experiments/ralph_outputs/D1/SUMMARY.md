# D1 — SUMMARY

**Task:** Run the opensre RFT/GRPO training for 50+ steps (current runs only 15–25)
to test whether the observed **+0.037 mean-reward trend** continues. Grounded in
`opensre-traj/train_rft.py` / `train_rft_v2.py`. Compute-capped (~15 min).

## What was delivered (all in `experiments/ralph_outputs/D1/`)
- **10 step files** (`01`–`10`) + this SUMMARY + `result.json`.
- **`artifacts/run_rft_50.sh`** — runnable 50-step launcher wrapping the **unmodified**
  `train_rft_v2.py` (group 6, lr 1e-5, tasks 0–9, append-only JSONL). `bash -n` PASS.
- **`artifacts/analyze_curve.py`** — pure-stdlib trend analyzer (delta, OLS slope,
  horizon projection, falsifiable continuing/flat/reversed verdict). 4/4 unit tests PASS.
- **`artifacts/train_d1_50step.jsonl` / `.log`** — REAL partial training curve, 9 steps,
  60 rollouts/step, from the live HUD/Tinker GPU backend (model `opensre-qwen3-8b-1e439a`).

## Result (the actual answer to the question)
The +0.037 trend is **real in sign and reproducible** but **within noise / flat**:
- Original v2 run (15 steps): delta +0.0371, OLS slope **+0.00174/step**, verdict flat.
- Fresh D1 run (9 steps): delta +0.0260, OLS slope **+0.00120/step**, verdict flat,
  projects to **~0.574 mean reward at step 50**.
- Per-step reward std ≈ 0.18 (SE of mean ≈ 0.025), so the slope moves the mean by
  < 1 SE over 15 steps — the climb is sub-noise, not a strong upward trend.

**Bottom line:** the trend *reproduces* but does not strongly *continue*; on these
near-ceiling tasks (start ~0.50) the curve is essentially flat. Recommended follow-up:
the harder real-outage cascades (model starts ~0.2 → real headroom) + multiple seeds.

## Blocker (documented, not faked)
Finishing all 50 steps is **compute-blocked**: ~75–90 s/step (60 rollouts/step on the
Tinker backend + transient 5xx retries) → 50 steps ≈ 60–75 min, far past the ~15-min
attended cap. Delivered: the launcher + a real 9-step partial curve; the remaining 41
steps were NOT fabricated. Complete via: `bash artifacts/run_rft_50.sh` (run unattended).

## Parallel safety
Zero edits to shared core files. All outputs are D1-namespaced.
