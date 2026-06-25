# D3 — 07 Test Results

## Unit tests — PASS (7/7)
```
$ python3 -m pytest test_same_scenario_groups.py -v
platform darwin -- Python 3.13.7, pytest-9.0.2
collected 7 items
test_same_scenario_groups.py::test_partition_groups_by_scenario PASSED   [ 14%]
test_same_scenario_groups.py::test_advantages_are_within_scenario PASSED [ 28%]
test_same_scenario_groups.py::test_degenerate_group_has_no_signal PASSED [ 42%]
test_same_scenario_groups.py::test_normalized_advantages PASSED          [ 57%]
test_same_scenario_groups.py::test_drop_singletons PASSED                [ 71%]
test_same_scenario_groups.py::test_variance_reduction_removes_between_scenario_term PASSED [ 85%]
test_same_scenario_groups.py::test_advantage_sign_corruption_under_mixing PASSED [100%]
============================== 7 passed in 0.01s ===============================
```

## Demo — PASS (real numbers, grounded in v2's ~0.5 mean / ~0.17 within-spread)
```
$ python3 demo_variance_reduction.py
metrics:
  mixed_msq            = 0.074762     # E[A^2] under mixed (pooled) baseline
  same_msq             = 0.031423     # E[A^2] under same-scenario baseline
  reduction_factor     = 2.379202     # 2.38x lower advantage second moment
  between_scenario_var = 0.043339     # Var(E[R|S]) removed by the fix
  within_scenario_var  = 0.031423     # E[Var(R|S)] retained (the real signal)
  n_rollouts=60  n_scenarios=10
  sign_flip_rate_mixed_vs_same = 0.2833   # 28% of rollouts' gradients pointed wrong under mixing
wrote demo_variance_reduction.json
```

## Total-variance invariant check — PASS
```
$ python3 -c "...invariant..."
mixed=0.074762  same+between=0.074762     # exact: Var(R) = E[Var(R|S)] + Var(E[R|S])
```

## Driver lazy-import / CLI — PASS (no HUD venv needed for --help)
```
$ python3 train_rft_same_scenario.py --help
usage: train_rft_same_scenario.py [-h] --model MODEL [--tasks TASKS]
                                  [--group GROUP] [--steps STEPS] [--lr LR]
                                  [--out OUT] [--smoke]
```

## Live GRPO smoke — BLOCKED (documented, not faked)
The `--smoke` path needs `../../../.venv-hud/bin/python`, a forked trainable Qwen slug
(`hud models fork Qwen/Qwen3-8B`), and the Tinker forward/backward endpoint. The full run is
~30 min and the endpoint intermittently 502s (hence the `_aretry` wrapper). This exceeds the
~15-min compute cap and is gated on external infra/credits. The driver IS runnable — the smoke
command is in its docstring — but a live training step was not executed here. See 09 for the
full blocker statement. No training numbers were fabricated.
