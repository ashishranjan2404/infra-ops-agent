# A2 — 04 Spec

## Artifact: `artifacts/run_ablation_fast.py`

### Purpose
Time-boxed, resumable wrapper that runs the 750-episode ablation with a faster proposer,
reusing the canonical engine without modifying any shared file.

### Imports (reuse, not reimplement)
```python
from rex.eval_pass_at_k import run_eval, print_report, CONDITIONS, summarize, \
                               pick_incidents, floor_check
```
`REPO` is computed 5 dirnames up from `__file__` (artifacts/A2/ralph_outputs/experiments/rl)
and prepended to `sys.path` so the module runs from anywhere.

### CLI
| flag | default | meaning |
|------|---------|---------|
| `--model` | `deepseek-v4-pro` | faster/cheaper proposer |
| `--per-family` | `10` | incidents per family -> 30 total |
| `--seeds` | `5` | seeds per incident |
| `--conditions` | all 5 | comma list; validated against `CONDITIONS` |
| `--max-workers` | `8` | episode concurrency |
| `--max-seconds` | `0` (unlimited) | wall-clock budget |
| `--out` | `artifacts/ablation_pass_at_k_<model>.json` | result path |

`target_episodes = len(conditions) * (3*per_family) * seeds`. Default = 5*30*5 = **750**.

### Control flow
```
target = 5*30*5
with Deadline(max_seconds):          # SIGALRM -> TimeoutError
    out = run_eval(model, conditions, per_family, seeds,
                   max_workers, ckpt=<out>.partial)   # checkpoints every 25 eps
    completed = True
except (TimeoutError, KeyboardInterrupt):
    out = summarize_partial(ckpt)     # real pass@k over completed eps only
out["a2_meta"] = {target, completed_episodes=count(per_incident_rewards),
                  fully_completed, wall_seconds, fast_model, note}
print_report(out); dump(out)
if fully_completed: remove(ckpt)
```

### Data contracts
- **Episode reward**: `float in [0,1]`, P0 deterministic judge.
- **Binary pass**: `reward >= THRESHOLD (0.8)`.
- **Result JSON** (matches `run_eval`'s schema so `rex/run_ablation_v2.py` can consume it):
  ```
  { model, label, threshold, seeds, incidents_by_family,
    by_condition: { <cond>: { overall: {n,passes,pass@1,ci95,pass@2,pass@5,
                                          mean_reward,reward_std},
                              by_family: {...}, per_incident_rewards: {name:[...]} } },
    floor_check: {empty_plan_max_reward, trap_max_reward, floor_ok},
    a2_meta: {target_episodes, completed_episodes, fully_completed, wall_seconds, ...} }
  ```
- **completed_episodes** = sum of `len(rewards)` across all `per_incident_rewards` — derived
  from actual data, never a time estimate (no double-count of aborted episodes).

### Test cases
1. **Compile**: `python3 -m py_compile run_ablation_fast.py` -> OK.
2. **Import resolution**: runs from repo root with `rex` importable.
3. **Smoke**: `--per-family 1 --seeds 1 --conditions zero_shot,best_of_n` produces a valid
   report dict with `completed_episodes <= 6`.
4. **Time-box honesty**: a short `--max-seconds` stops, flushes, and reports
   `fully_completed=false` with `completed_episodes` matching the checkpoint length.
5. **Empty-checkpoint degrade**: time-box fires before 25 eps -> empty valid report, no crash.
6. **Schema compat**: output loads in `rex/run_ablation_v2.py::aligned_rewards` without error.
