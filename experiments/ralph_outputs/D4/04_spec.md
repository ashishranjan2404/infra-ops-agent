# D4 — 04 Spec

## Data structures

### `HarnessInLoopConfig` (dataclass)
| field | type | default | meaning |
|---|---|---|---|
| `unsafe_penalty` | float | 0.25 | reward subtracted per blocked/unsafe action proposed |
| `reward_floor` | float | -1.0 | lower clamp on shaped reward |
| `filter_unsafe` | bool | True | drop blocked actions before world execution (is_safe always does) |
| `count_only_executed_block` | bool | True | only penalize actions the model actually proposed |

### `ShapedReward` (dataclass)
`reward`(float, the scalar fed to the trainer), `base_reward`(float), `n_proposed`(int),
`n_blocked`(int), `n_applied`(int), `penalty`(float), `safe_fraction`(float in [0,1]),
`per_action`(list of `{action, allowed: bool, reason: str}`), `resolved`(bool).
`.to_dict()` -> JSON-serializable.

## Function signatures
```python
def gate_plan(plan: dict, scenario: Scenario) -> tuple[list, int, int]
    # -> (per_action, n_blocked, n_applied); runs each action through REAL is_safe
    #    against the same evolving state (applied_tools) that rex.harness.run_plan uses.

def harness_in_loop_reward(plan: dict, scenario: Scenario, base_reward: float,
                           cfg: HarnessInLoopConfig | None = None) -> ShapedReward

def rollout_reward(plan: dict, scenario_name: str,
                   cfg: HarnessInLoopConfig | None = None,
                   base_reward: float | None = None) -> ShapedReward
    # end-to-end: load_scenario -> (run real sim for base if None) -> shape.
```

## Reward contract
`shaped = max(cfg.reward_floor, base_reward - cfg.unsafe_penalty * n_blocked)`
`safe_fraction = n_applied / n_proposed` (1.0 for empty plan).
`is_safe` NEVER executes an unsafe action regardless of config (safety invariant).

## `plan` format (matches rex.harness.run_plan)
`{"actions": [{"tool": str, "args": {"target": str, ...}}, ...]}`

## Test cases (`test_harness_in_loop.py`)
1. trap action blocked on real `gcp_service_control` (scale_deployment treats ruled-out
   'saturation') → blocked; fix `modify_network_policy` allowed.
2. unsafe plan penalized: base 1.0, penalty 0.25 → reward 0.75, safe_fraction 0.5.
3. safe plan keeps base reward (0.8 → 0.8, penalty 0).
4. penalty scales: `singleton_node_notready` drain+cordon both blocked → penalty 0.4.
5. reward floor clamps: penalty 5.0×2 → clamped to -1.0, not -10.
6. empty plan is safe by definition (safe_fraction 1.0).
7. end-to-end `rollout_reward` runs real sim, trap still penalized.

## Config file (`harness_in_loop.yaml`)
`reward_shaping`, `safety_layers`, `train_scenarios` (mix incl. held-out escalation),
`backend` (HUD/Tinker defaults mirroring train_rft_v2.py).

## Wire-in (`.patch`, NOT applied)
Minimal diff into `train_rft_v2.py`: replace `rewards = [r.reward for r in batch]` with
`rewards = [_shape(r) for r in batch]`, attach shaped rewards onto the batch runs, feed to
`trainer.step`. Integration point: HUD env must surface `run.plan` + `run.scenario_name`.
