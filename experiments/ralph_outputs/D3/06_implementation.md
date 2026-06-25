# D3 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/D3/artifacts/`, no core edits)

### `same_scenario_groups.py` (118 LOC, stdlib only)
- `ScenarioGroup` dataclass: `rewards`, `mean_reward`, `reward_std`, `advantages()`,
  `is_degenerate` (flags zero-spread groups — surfaces SRE's "necessary-not-sufficient" point).
- `group_rollouts_by_scenario(batch, key=, drop_singletons=)` — first-seen-deterministic
  partition into per-scenario groups. Robust key resolver: `.scenario_id → .scenario →
  .task.id → .task.name → .task_id → dict keys → repr` (real HUD `Run` hits `.task.id`).
- `grpo_advantages(rewards, normalize=)` — `A_i = r_i - mean(r)` (optionally `/std`).
- `gradient_variance_reduction_factor(per_scenario_rewards)` — makes the variance claim
  numeric via law of total variance: `Var(R) = E[Var(R|S)] + Var(E[R|S])`. Returns
  `mixed_msq`, `same_msq`, `between_scenario_var`, `within_scenario_var`, `reduction_factor`.

### `train_rft_same_scenario.py` (proposed train_rft_v3 — additive copy, NOT a core edit)
The ONLY substantive change vs `opensre-traj/train_rft_v2.py`:
- **v2 (lines 89-100):** one `ts.run(agent, group=G)` over a *multi-scenario* Taskset → a GRPO
  group can mix scenarios → advantage baseline soaks up scenario difficulty.
- **v3 (this file):** build ONE single-scenario `Taskset` per index; per step, loop scenarios,
  `ts_i.run(group=G)` → each block is a pure same-scenario group; concatenate; one
  `trainer.step(batch, group_size=G)`. Logs `mean_within_scenario_spread` (the trainable signal
  retained) and `cross_scenario_spread_removed` (the nuisance variance deliberately dropped).
- HUD imported lazily inside `run()` → `--help`/tests run without `.venv-hud`.

> Note for the maintainer: this is the proposed change to fold back into core
> `opensre-traj/train_rft_v2.py`. Per the Ralph-Loop parallel-safety rule I did NOT edit the
> original; the diff is described above and the runnable v3 driver is the artifact.

### `test_same_scenario_groups.py` — 7 unit tests (see 07).
### `demo_variance_reduction.py` → `demo_variance_reduction.json` — grounded numeric demo.

## Why this reduces gradient variance (the explanation)
GRPO uses `g = E[A·∇logπ]`, `A_i = r_i − b`. With a **mixed** group the baseline `b` is the
pooled mean, so `A` carries the full `Var(R) = E[Var(R|S)] + Var(E[R|S])`. The second term,
`Var(E[R|S])`, is **scenario difficulty** — it has nothing to do with which rollout was better,
yet it inflates `E[A^2]` (a proxy upper bound on the per-sample gradient variance, with `∇logπ`
held fixed). **Same-scenario** grouping sets `b = E[R|S=s]`, deleting `Var(E[R|S])` exactly and
leaving only the informative within-scenario term `E[Var(R|S)]`. Concretely worse: under mixing,
the *worse* rollout on an easy scenario gets a *positive* advantage and the *better* rollout on a
hard scenario gets a *negative* one — the gradient pushes the wrong way. The demo measures this
as a 28% advantage **sign-flip rate** on real-grounded stats (mean≈0.5, within-std≈0.17).

## Verified numbers (real run output)
- 7/7 unit tests pass.
- Demo: `reduction_factor = 2.38x` (E[A^2] 0.0748 → 0.0314), `between_scenario_var = 0.0433`,
  `within = 0.0314`, **sign-flip rate 28%**. Total-variance invariant holds exactly:
  `mixed (0.074762) == same + between (0.074762)`.
