# B10 — 01 Plan: RFT learning curve (pass@1 vs training steps)

## Objective
Produce a learning curve plotting **pass@1 vs GRPO training step** for the opensre RFT run,
grounded in the real training scripts and run logs, as a reusable matplotlib harness.

## Grounding (what actually exists)
- `opensre-traj/train_rft.py` — GRPO loop. Each step appends a JSONL line:
  `{"step", "mean_reward", "n", "rewards":[...], "loss"}`.
- `opensre-traj/train_rft_v2.py` — v2 (deterministic mechanism reward); adds `"reward_std"`.
- Real logs present in `opensre-traj/runs/`:
  - `train_qwen3-8b.jsonl` (25 steps, n=24/step) — the documented FLAT baseline (0.522→0.491).
  - `train_qwen3-8b_v2.jsonl` (15 steps, n=40/step).
  - `train_qwen3-30b.jsonl` (14 steps, n=24/step).
- The reward is a **continuous weighted grader score in [0,1]** (hud_env_static / hud_env_v2),
  NOT a binary pass/fail. So pass@1 must be DERIVED via a success threshold.

## pass@1 definition (reuse the repo convention)
`rex/eval_pass_at_k.py:43` + `experiments/compute_pass_at_k.py:39` define
`THRESHOLD = 0.8` and `binary_pass(reward) = reward >= 0.8`.
- A rollout passes iff `reward >= THRESHOLD`.
- `pass@1(step) = (#rollouts >= THRESHOLD) / n` — the standard single-sample pass rate
  (each GRPO rollout is one i.i.d. attempt; the per-rollout indicator's mean IS pass@1).
- Report a Wilson 95% CI per step (small n=24/40).

## Files to create (all task-namespaced — NO shared-core edits)
- `artifacts/learning_curve.py` — parser + pass@1 derivation + matplotlib plot + CSV export.
- `artifacts/test_learning_curve.py` — self-tests (threshold, boundary, robustness, real logs).
- `artifacts/learning_curve.png` + `.csv` — outputs at the canonical τ=0.8.
- `artifacts/learning_curve_t065.png` + `.csv` — companion at τ=0.65 (inside the reward dist).

## Dependencies
Python 3.13, matplotlib 3.11 (present). stdlib json/csv/glob/math. No network, no GPU.

## Risks
1. **Threshold has no signal.** Mid-training Qwen rarely clears reward 0.8 → pass@1 flat at 0
   under the canonical threshold. Mitigation: keep the honest τ=0.8 curve AND a τ=0.65 curve
   that sits inside the reward distribution so per-step movement is visible.
2. Logs log `rewards` but not pass@1 → derivation must be explicit and documented.
3. GRPO `rewards` groups span multiple scenarios → pass@1 is over the mixed batch, not per-task.

## Success criteria
- Script parses all real logs without error; derives pass@1 per step with the documented rule.
- Produces a valid PNG learning curve + CSV; self-tests pass.
- No shared core file edited; `compute_pass_at_k` math reused (mirrored), not modified.
