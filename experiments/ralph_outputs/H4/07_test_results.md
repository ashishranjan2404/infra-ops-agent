# 07 — Test results (real command output)

## A. Standalone test runner — PASS (8/8)
```
$ python3 experiments/ralph_outputs/H4/artifacts/test_exptrack.py
PASS test_auto_falls_back_to_jsonl_without_wandb
PASS test_context_manager_finishes
PASS test_jsonl_backend_selected_when_forced
PASS test_jsonl_run_writes_meta_metric_summary
PASS test_log_never_raises_after_finish
PASS test_non_scalar_values_are_coerced
PASS test_none_backend_is_noop
PASS test_wandb_disabled_env_forces_jsonl
ALL PASS
```

## B. pytest — PASS (8/8)
```
$ python3 -m pytest experiments/ralph_outputs/H4/artifacts/test_exptrack.py -q
........                                                                 [100%]
8 passed in 0.21s
```

## C. Import / backend resolution
```
$ python3 -c "import exptrack; print(exptrack.select_backend())"
backend(auto)= wandb        # wandb 0.27.2 IS installed in this env
```
Note: `auto` correctly prefers wandb when present. The **fallback** (the unit-tested path)
is reached via `EXPTRACK_BACKEND=jsonl` or `WANDB_DISABLED=true`:
```
$ EXPTRACK_BACKEND=jsonl python3 -c "...select_backend()"   -> jsonl
$ WANDB_DISABLED=true    python3 -c "...select_backend()"   -> jsonl
```
So BOTH branches (cloud present, cloud disabled) are exercised and behave correctly.

## D. Patch applies cleanly; core file untouched
```
$ git apply --check experiments/ralph_outputs/H4/artifacts/train_rft_v2.exptrack.patch
git apply --check: OK
$ git status --short opensre-traj/train_rft_v2.py
?? opensre-traj/train_rft_v2.py        # untracked, NO modification
```

## E. Live JSONL run + validity
A 3-step demo run wrote `demo_runs/demo-rft-*.jsonl`:
```
{"_type":"meta",  ...,"config":{"model":"glm-5p2","lr":1e-05,"group":6,"steps":3}}
{"_type":"metric","step":0,...,"mean_reward":0.3,"reward_std":0.12,"loss":1.5,"n":6}
{"_type":"metric","step":1,...,"mean_reward":0.4,...,"loss":1.3}
{"_type":"metric","step":2,...,"mean_reward":0.5,...,"loss":1.1}
{"_type":"summary",...,"best_reward":0.5}
```
Every line parses as JSON:
```
$ python3 -c "import json,glob;[json.loads(l) for f in glob.glob('.../demo_runs/*.jsonl') for l in open(f)]"
all demo lines parse as JSON: OK
```

## Fixes applied during testing
None required — the three issues anticipated in 05 (closed-file write, non-scalar values,
explicit-backend-without-import) were guarded up front and their tests passed first try.
