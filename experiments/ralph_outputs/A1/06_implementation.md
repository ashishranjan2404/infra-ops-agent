# A1 — 06 Implementation

## What I built
A single task-namespaced runner that produces the **full 42-incident** pass@k table by
reusing the existing pipeline unmodified.

### Artifact: `artifacts/run_full_pass_at_k.py`
- Adds `sys.path.insert(REPO)` (the runner lives 4 dirs deep and `rex` isn't otherwise importable).
- Imports `run_eval`, `print_report`, `THRESHOLD` from `rex/eval_pass_at_k.py` **without editing it**.
- Calls `run_eval(model, conditions, per_family=None, seeds, ...)`. `per_family=None` is the
  load-bearing flag: `pick_incidents(None)` returns *all* incidents per family -> 42 total
  (vs the default `--per-family 5` slice = 15).
- Redirects the crash-survival checkpoint and final JSON into `A1/artifacts/`
  (`full_pass_at_k_<model>.json[.partial]`) so it never races the shared
  `experiments/results/` dir that other workers / a prior run touch.
- Tags the output with `n_incidents` and `full_set: true`, and asserts
  `n_incidents == 42` and `floor_check.floor_ok` at the end.

### Why no new estimator code
`experiments/compute_pass_at_k.py` is the single source of truth for `pass_at_k` (unbiased
Chen estimator), `wilson_ci`, and `binary_pass`; `rex/eval_pass_at_k.py` already imports them
and already serializes per-incident reward vectors + per-family splits + the floor check.
Re-implementing any of that would risk divergence. The correct deliverable is the thin wrapper.

## Proposed core change (NOT applied — documented per parallel-safety rules)
The core sweep orders jobs **condition-major** (`for cond -> for name -> for seed`) and uses
`ThreadPoolExecutor.map`, whose *ordered* result iteration blocks the first condition's tail
before later-condition results are recorded to the checkpoint. For a future single-source edit
(owned by whoever owns `rex/eval_pass_at_k.py`), switching to `as_completed` would let the
checkpoint advance across all conditions concurrently and make a timeout degrade gracefully
across conditions instead of front-loading zero_shot. I did NOT edit the core file; this is
recorded here as a recommendation only.

## Pre-flight done offline (no API)
- `floor_check` over all 42 incidents:
  `{"empty_plan_max_reward":0.0,"trap_max_reward":0.1,"threshold":0.8,"floor_ok":true}`.
- Family sizes confirmed: simple=12, cascade=20, novel=10 (=42).

## Run
`python3 experiments/ralph_outputs/A1/artifacts/run_full_pass_at_k.py --model glm-5p2 --seeds 3
 --conditions zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle --max-workers 10`
(gateway model glm-5p2, deterministic judge). Result + numbers in 07/08.
