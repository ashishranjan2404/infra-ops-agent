# D4 — 07 Test Results

## Unit tests — PASS (7/7)
```
$ python3 -m pytest experiments/ralph_outputs/D4/artifacts/test_harness_in_loop.py -v
collected 7 items
test_trap_action_is_blocked_on_real_scenario PASSED   [ 14%]
test_unsafe_plan_is_penalized PASSED                  [ 28%]
test_safe_plan_keeps_base_reward PASSED               [ 42%]
test_penalty_scales_with_unsafe_count PASSED          [ 57%]
test_reward_floor_clamps PASSED                       [ 71%]
test_empty_plan_is_safe_by_definition PASSED          [ 85%]
test_rollout_reward_end_to_end_runs_real_sim PASSED   [100%]
============================== 7 passed in 0.06s ===============================
```

## Standalone demo — runs the REAL sim + harness
```
$ cd /tmp && python3 .../D4/artifacts/harness_in_loop.py
reward 0.75  base 1.0  n_blocked 1  resolved True
```
On `gcp_service_control`: the `scale_deployment(service-control)` trap is blocked by the
REAL `is_safe` with reason "it treats 'saturation', a ruled-out cause (the real root is
'config_error')"; the `modify_network_policy` fix is applied; the sim resolves (base 1.0);
shaped reward 1.0 − 0.25 = 0.75. Confirms filtering AND penalty are both active.

## Import-path check — PASS (both)
- via pytest from repo root (cwd on sys.path): pass.
- standalone from `/tmp` (uses `*([os.pardir]*4)` to find repo root): pass.

## YAML parse — PASS
`yaml.safe_load` OK; keys `reward_shaping, safety_layers, train_scenarios, backend`;
6 training scenarios resolve via `rex.harness.load_scenario`.

## Patch — syntactic review only
`train_rft_harness_in_loop.patch` is documentation (not applied; shared core file). Reviewed
for correct insertion points against the current `train_rft_v2.py` (the `batch = session.runs
[start:]` / `trainer.step` lines exist as referenced).

## BLOCKER — live GRPO training NOT run
A real harness-in-the-loop RFT run requires the HUD/Tinker backend: a forked trainable Qwen
slug (`hud models fork Qwen/Qwen3-8B`), `HUD_API_KEY`, and the `.venv-hud` (Python 3.12)
interpreter — and 30 GRPO steps far exceed the ~15 min compute cap. Per the no-fabrication
rule, NO training curves are reported. The deliverable is the tested, real reward path + the
documented wire-in; the backend run is the only blocked piece.
