# D2 — 01 Plan

## Objective
Run RFT (GRPO/RLVR) with Qwen-14B on the opensre incident env. The meeting flagged
that 8B "may be too small" — the `opensre-qwen3-8b` v2 run was flat
(`runs/train_qwen3-8b_v2.jsonl`: mean_reward 0.50 → 0.54 over 15 steps, reward_std ~0.19).
A larger base is the natural next lever. Compute cap ~15 min: deliver a runnable
Qwen-14B training **config + launcher** plus a documented blocker if the backend/GPU
isn't reachable. Do not fabricate metrics.

## Approach
- Ground in `opensre-traj/train_rft.py` and `opensre-traj/train_rft_v2.py` (the proven
  GRPO loop: rollouts → reward → forward/backward → JSONL, with 5xx retry, within-group
  spread logging, and `--reset-head`).
- The training loop itself is good and shared — do NOT rewrite it. Build a thin
  **additive launcher** that (a) selects the larger base, (b) preflights the HUD Tinker
  gateway so we never train against a model that doesn't exist, (c) delegates to
  `train_rft_v2.run()`.
- Verify on the real gateway which Qwen sizes are actually trainable (Tinker provider).

## Files to create (task-namespaced — no core edits)
- `artifacts/train_rft_qwen14b.py` — the launcher (imports `train_rft_v2`, never edits it).
- `artifacts/qwen14b_train.config.yaml` — canonical flag set + blocker record.
- `artifacts/runs/` — output dir for any JSONL (empty unless a real run executes).

## Dependencies
- `.venv-hud` (Python 3.12, hud SDK 0.6.6), `HUD_API_KEY` (present, len 42).
- HUD Tinker gateway reachability for fork + forward/backward.

## Risks
- **Primary risk (materialized): Qwen-14B may not exist on the Tinker gateway.** If so,
  a literal 14B run is impossible; mitigate with a documented substitute (closest dense
  rung above 8B) and a preflight that fails loud.
- Real 30-step GRPO on a 27B/30B base is hours of paid compute — out of the 15-min cap.
  Deliver launcher+config+preflight, not fabricated curves.

## Success criteria
1. Launcher compiles, `--help` works, YAML parses.
2. `--preflight` hits the real gateway and correctly reports 14B availability + verifies
   the chosen base is trainable (exit 0 only when it is).
3. Launcher imports the core trainer without modifying any shared core file.
4. Blocker (if any) documented honestly; zero fabricated metrics.
