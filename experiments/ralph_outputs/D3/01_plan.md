# D3 — 01 Plan

## Objective
Implement **same-scenario GRPO group batching** for the opensre RFT training loop
(the third fix from Table 1), explain *why* it reduces gradient variance, and prove
it with a runnable demo + unit tests. Do NOT edit shared core files.

## Where this lives in the real code
- `opensre-traj/train_rft_v2.py` docstring (lines 11-13) names the bug explicitly:
  > "(likely) GRPO groups spanning DIFFERENT scenarios so the advantage reflects
  > per-scenario difficulty, not which rollout was better."
- The training loop (`train_rft_v2.py:89-100`) runs `ts.run(agent, group=G, job=session)`
  over a **multi-scenario** Taskset, then `trainer.step(batch, group_size=G)`. When the
  taskset holds K scenarios, a GRPO group of size G can be filled from rollouts of
  *different* incidents, so the advantage baseline (group mean) mixes scenario difficulty
  with rollout quality.

## Approach
1. Add a standalone, HUD-free module `same_scenario_groups.py`:
   - `group_rollouts_by_scenario(batch)` — partition a flat batch into per-scenario groups.
   - `grpo_advantages(rewards)` — group-relative (mean-centered) advantage.
   - `gradient_variance_reduction_factor(per_scenario_rewards)` — make the variance claim
     numeric via the law-of-total-variance decomposition (between- vs within-scenario).
2. Add `train_rft_same_scenario.py` — an additive copy of `train_rft_v2.py` whose ONLY
   change is: one single-scenario Taskset per index, looped per step, so every
   `trainer.step` group is pure same-scenario.
3. Unit-test the math + a synthetic demo that reports the variance-reduction factor and
   the advantage **sign-flip rate** (rollouts whose gradient direction was wrong under mixing).

## Files to create (all task-namespaced, no core edits)
- `artifacts/same_scenario_groups.py`
- `artifacts/train_rft_same_scenario.py`
- `artifacts/test_same_scenario_groups.py`
- `artifacts/demo_variance_reduction.py` (+ generated `demo_variance_reduction.json`)

## Dependencies
- stdlib only for the module/tests/demo (statistics, dataclasses).
- The training driver imports HUD lazily — only needed for a LIVE run on `.venv-hud`.

## Risks
- A live GRPO run needs a forked Qwen slug + the Tinker trainer + ~30 min; over the 15-min
  cap and gated by external infra. Mitigation: ship a runnable driver + a deterministic
  numeric demo that isolates the variance mechanism; document the live-run blocker.
- Same-scenario grouping does NOT help a scenario with zero within-group spread (degenerate
  group). Must surface this honestly (it's an orthogonal fix — that's what D2/v2's graded
  reward addresses).

## Success criteria
- `pytest` on the new test file passes.
- Demo prints a >1x variance-reduction factor with the total-variance decomposition matching.
- Driver `--help` runs without the HUD venv (lazy import verified).
- Clear written explanation tying the fix to the policy-gradient variance.
