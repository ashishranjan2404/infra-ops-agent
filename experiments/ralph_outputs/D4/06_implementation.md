# D4 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/D4/artifacts/`)

### `harness_in_loop.py` — the harness-in-the-loop reward path
- Imports the REAL safety harness verbatim: `is_safe`, `build_state`, `load_scenario`,
  `run_plan`, `Scenario` from `rex.harness`. Training-time safety == eval-time safety.
- `gate_plan(plan, scenario)` runs each candidate action through `is_safe` against the same
  evolving `applied_tools` state `run_plan` uses; returns per-action allow/reason + counts.
  (World is scaffolded but not advanced — gating decisions don't read settled metrics; see
  `05_ouroboros.md` Engineer A.)
- `harness_in_loop_reward(plan, scenario, base_reward, cfg)` ->
  `shaped = max(floor, base_reward - unsafe_penalty * n_blocked)`, returning a `ShapedReward`
  with `n_blocked`, `safe_fraction`, and a per-action breakdown.
- `rollout_reward(plan, scenario_name, cfg, base_reward=None)` — end-to-end: loads the
  scenario, runs the REAL sim (`run_plan`) for a base reward when none is supplied, then shapes.
- `__main__` demo prints the shaped reward JSON for a real `gcp_service_control` plan.

### `harness_in_loop.yaml` — config
Shaping knobs (`unsafe_penalty`, `reward_floor`, ...), the active safety layers, a training
scenario mix with within-group spread (simple leaves + cascades + the held-out
`singleton_node_notready` escalation), and the HUD/Tinker backend params (mirroring
`train_rft_v2.py`). The shaped scalar replaces the raw env reward fed to `trainer.step`.

### `test_harness_in_loop.py` — unit tests on the reward path (7 tests)
Trap blocked on a real scenario; unsafe plan penalized; safe plan keeps base; penalty scales;
floor clamps; empty plan safe; end-to-end `rollout_reward` runs the real sim. All pass.

### `train_rft_harness_in_loop.patch` — documented wire-in (NOT applied)
Minimal diff into `opensre-traj/train_rft_v2.py`: shape each batch run's reward via
`harness_in_loop_reward` before `trainer.step`. Provided as a `.patch` because
`train_rft_v2.py` is a shared core file (real-artifact rule) and a live GRPO run is blocked
(see 07/09).

## Shared-core-file changes proposed but NOT made
- `opensre-traj/train_rft_v2.py`: see the `.patch`. Integration point — the HUD env
  (`hud_env_v2.py`) must surface the parsed `plan` + `scenario_name` per rollout; if it only
  returns a scalar, a one-line change in its `evaluate()` is needed (documented in 09).

## How the harness is "in the loop"
Two distinct effects vs. LLM-alone RFT: (1) **filtering** — `is_safe` removes unsafe actions
from world execution during rollout; (2) **penalty** — the reward subtracts per proposed
unsafe action, so the gradient sees the cost. This is Wenji's LLM + harness, not LLM alone.
