# D14 — 04 Spec

## Data: the 42-incident task file (`tasks_42.json`)

```json
{
  "name": "opensre-42-incident",
  "env_module": "hud_env_v2.py",
  "env_template": "investigate_v2",
  "scenario_arg": "scenario_id",
  "count": 42,
  "n_canonical": 34, "n_variants": 8,
  "n_real_postmortem": 19, "n_synthetic": 23,
  "corpus": "<abs path to out/trajectories.jsonl>",
  "tasks": [
    {"index": 0, "scenario_id": "001-oom_kill", "category": "resource_exhaustion",
     "difficulty": 3, "kind": "canonical", "origin": "synthetic"},
    ...
  ]
}
```

Invariants: `len(tasks) == count == 42`; scenario_ids unique; every scenario_id ∈ corpus;
`kind ∈ {canonical, variant}`; `origin ∈ {real_postmortem, synthetic}`; `difficulty ∈ {3,4,5}`.

## Selection algorithm (`assemble.assemble(recs, n=42)`)
```
canonical = sorted(s for s in recs if not re.search(r"-s\d+$", s))   # 34
if n <= len(canonical): chosen = canonical[:n]
else:
    chosen = canonical
    need = n - 34                                                     # 8
    by_base = {base: [variants...]}                                   # from -sNNN ids
    for base in sorted(by_base):                                      # 001..015
        chosen.append(max(variants_of_base))                         # most-perturbed
        if len(extra) == need: break
```
Deterministic (sorted everywhere); reproducible; no network.

## Function signatures (`assemble_tasks.py`)
- `load_corpus(corpus: Path) -> dict[str, dict]`
- `_difficulty(rec) -> int`  (reads `difficulty`, falls back to `scenario_difficulty`, default 3)
- `_category(rec) -> str`    (reads `answer.root_cause_category`)
- `assemble(recs, n=42) -> list[dict]`
- CLI: `--n 42 --out tasks_42.json --corpus <path>`; validates uniqueness + membership; exits non-zero on failure.

## Config schema (`train_rft_42.yaml`)
| key | type | meaning |
|---|---|---|
| name | str | job/taskset name prefix |
| model | str | trainable open slug (forked Qwen); override `--model` |
| env_module | str | `hud_env_v2.py` (relative to opensre-traj/) |
| task_file | str | `tasks_42.json` (relative to config dir) |
| tasks | "all" \| "i,j,k" | all 42, or 0-based indices into the file |
| group | int | GRPO rollouts per group |
| steps | int | optimizer steps |
| learning_rate | float | lr |
| reset_head | bool | roll trainable head back before step 0 (reward changed) |
| curriculum | bool | order tasks by (difficulty, index) easy->hard |
| out | str | jsonl reward log (relative to opensre-traj/) |
| smoke | map | overrides applied when `--smoke` (tasks/group/steps) |

## Launcher contract (`train_rft_42.py`)
- `load_config(path, smoke) -> dict` — merges `smoke:` overrides on top when `--smoke`.
- `resolve_task_ids(cfg, cfg_dir) -> (ids, rows)` — applies `tasks` selection + curriculum sort.
- `build_tasks(ids) -> (hud_tasks, env)` — chdir opensre-traj, import `hud_env_v2`,
  assert all ids ∈ `SCENARIOS`, return `[investigate_v2(scenario_id=s) for s in ids]`.
- `run(cfg, ids, rows, model)` — Job.start -> per step: `ts.run` rollouts -> `trainer.step`;
  logs `{step, mean_reward, reward_std, n, loss}` per line; transient-5xx retry wrapper.
- `--dry-run` — validates ids against corpus by reading trajectories.jsonl directly
  (NO `hud` import), prints curriculum order; exit 0 iff all ids resolve.

## Test cases
1. `assemble_tasks.py` -> exactly 42 unique ids; counts 34/8 and 19/23. **(automated assert)**
2. `--dry-run` (full) -> "42 tasks", "missing=[]", curriculum first = difficulty-3. **(grep)**
3. `--smoke --dry-run` -> 2 tasks resolved. **(grep)**
4. `py_compile` both scripts; `yaml.safe_load` the config. **(automated)**
5. live `--smoke` in `.venv-hud` -> rollouts -> reward -> step -> log line. **(real run)**
