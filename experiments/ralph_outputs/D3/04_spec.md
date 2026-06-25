# D3 — 04 Spec

## Module `same_scenario_groups.py` (stdlib only)

### Data structures
```python
@dataclass
class ScenarioGroup:
    scenario_id: str
    rollouts: list           # HUD Run / dict / any with .reward
    # properties: rewards, size, mean_reward, reward_std,
    #             advantages(normalize=False), is_degenerate
```

### Function signatures
```python
def group_rollouts_by_scenario(
    batch: Iterable[Any],
    key: Callable[[Any], str] | None = None,   # default: .task.id / .task_id / dict keys
    min_group: int = 2,
    drop_singletons: bool = False,
) -> list[ScenarioGroup]

def grpo_advantages(rewards: Sequence[float],
                    normalize: bool = False, eps: float = 1e-8) -> list[float]
    # A_i = r_i - mean(r)  [ /(std(r)+eps) if normalize ]

def gradient_variance_reduction_factor(
    per_scenario_rewards: dict[str, Sequence[float]]
) -> dict   # keys: mixed_msq, same_msq, reduction_factor,
            #       between_scenario_var, within_scenario_var, n_rollouts, n_scenarios
```

### Scenario-key resolution order
`.scenario_id` → `.scenario` → `.task.id` → `.task.name` → `.task_id` → dict keys
(`scenario_id|scenario|task_id|id`) → `repr`. Covers HUD `Run` (has `.task`), our
test `_Run` (has `.task_id`), and plain dicts.

### Variance metric contract (the math, testable)
For pooled rewards R with scenario label S:
- `mixed_msq` = mean over all rollouts of `(r - global_mean)^2`  = `Var(R)`
- `same_msq`  = mean over all rollouts of `(r - scenario_mean)^2` = `E[Var(R|S)]`
- `between_scenario_var` = `mixed_msq - same_msq` = `Var(E[R|S])`  (must be ≥ 0)
- `reduction_factor` = `mixed_msq / same_msq`
Invariant (law of total variance): `mixed_msq == same_msq + between_scenario_var`.

## Driver `train_rft_same_scenario.py`
- Mirrors `train_rft_v2.py` arg surface: `--model --tasks --group --steps --lr --out --smoke`.
- HUD imported **inside** `run()` (lazy) so `--help`/tests don't need `.venv-hud`.
- Per step: for each scenario index, build a 1-task `Taskset`, `ts_i.run(group=G, job=session)`,
  collect that contiguous block as a pure same-scenario sub-batch; concatenate; one
  `trainer.step(batch, group_size=G)`.
- Log per step: `mean_reward`, `mean_within_scenario_spread`,
  `cross_scenario_spread_removed`, `per_scenario_within_spread[]`, `n_scenario_groups`, `n`, `loss`.

## Test cases (`test_same_scenario_groups.py`)
1. partition groups by scenario (sizes + deterministic first-seen order).
2. advantages mean to 0 within a scenario; correct magnitudes.
3. degenerate group → all-zero advantages + `is_degenerate` True.
4. normalized advantages → ±1 for a 2-element group.
5. `drop_singletons` removes size-1 groups.
6. variance reduction: identical within-spread, different difficulty → `same<mixed`,
   factor>5, `between==Var(means)`, `within==within_std^2`.
7. sign-corruption: mixed baseline flips the advantage sign on easy/hard rollouts;
   same-scenario restores correct signs.

## Demo output `demo_variance_reduction.json`
```json
{"setup": {...}, "metrics": {...}, "sign_flip_rate_mixed_vs_same": <float>,
 "interpretation": "<one-paragraph plain-English>"}
```

## File formats
- All artifacts under `experiments/ralph_outputs/D3/artifacts/`.
- JSON demo output: 2-space indent, deterministic (seed=0).
