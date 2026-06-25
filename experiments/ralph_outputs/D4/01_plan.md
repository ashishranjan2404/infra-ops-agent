# D4 — 01 Plan

## Objective
Run RFT with the harness **in the loop** (Wenji's ask: LLM + harness, not LLM alone).
The baseline RFT (`opensre-traj/train_rft*.py`) computes reward only AFTER a whole plan
runs, so unsafe actions hurt only via a delayed, noisy downstream score. We want the
REAL safety harness (`rex/harness.py::is_safe`) to **filter and penalize** unsafe actions
DURING rollout collection, so the policy gradient sees the cost of proposing them.

## Approach
1. Build a self-contained reward module (`harness_in_loop.py`) that reuses the
   production `is_safe`/`build_state`/`load_scenario`/`run_plan` verbatim — training-time
   safety semantics are byte-identical to eval-time.
2. `harness_in_loop_reward(plan, scenario, base_reward, cfg)`:
   - gate every action through `is_safe` against the same evolving state `run_plan` uses;
   - `shaped = max(floor, base_reward - unsafe_penalty * n_blocked)`;
   - return a breakdown (per-action allowed/reason, n_blocked, safe_fraction).
3. A YAML config (`harness_in_loop.yaml`) for the shaping knobs + training scenarios.
4. A unit test (`test_harness_in_loop.py`) on the harness-in-loop reward path.
5. A documented `.patch` showing the minimal wire-in into `train_rft_v2.py` (NOT applied —
   shared core file).

## Files to create (all task-namespaced under artifacts/)
- `artifacts/harness_in_loop.py` — reward module.
- `artifacts/harness_in_loop.yaml` — config.
- `artifacts/test_harness_in_loop.py` — unit tests.
- `artifacts/train_rft_harness_in_loop.patch` — documented wire-in.

## Dependencies
- `rex/harness.py` (is_safe, build_state, load_scenario, run_plan) — REUSED, not edited.
- `sim/engine.py` (World) — for state scaffolding.
- `pytest`. No network. Training backend (HUD/Tinker) is NOT exercised (compute cap).

## Risks
- Training backend (HUD Tinker GRPO) needs a forked Qwen slug + HUD_API_KEY + .venv-hud;
  a live run is out of the ~15 min cap and is documented as a blocker.
- Wire-in depends on the HUD env surfacing the parsed plan + scenario id per rollout.

## Success criteria
- Reward module imports the REAL harness and gates real scenarios.
- Unit tests pass (trap penalized, safe plan keeps base reward, penalty scales, floor clamps).
- Standalone demo runs the real sim and shows a trap blocked + penalized.
- No shared core file edited; blocker documented honestly.
