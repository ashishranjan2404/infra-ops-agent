# D14 — 06 Implementation

## Artifacts created (all under `experiments/ralph_outputs/D14/artifacts/`)

| file | what it is |
|---|---|
| `assemble_tasks.py` | dataset-assembly script: corpus -> deterministic 42-incident selection -> `tasks_42.json`, with self-validation |
| `tasks_42.json` | the **assembled 42-incident task file** (the deliverable dataset) |
| `train_rft_42.yaml` | the **runnable RFT config** that uses all 42 incidents as the GRPO task set |
| `train_rft_42.py` | config-driven GRPO launcher that builds the Taskset from explicit scenario_ids |
| `smoke_run.jsonl` | archived reward log from a REAL live smoke run (evidence) |

## What was built

**1. Assembly (`assemble_tasks.py`).** Reads the opensre corpus
(`opensre-traj/out/trajectories.jsonl`, 319 records), partitions canonical (34) vs
variant (`-sNNN`) ids, and deterministically selects 42 = all 34 canonical + the
most-perturbed variant of 8 distinct synthetic bases (001-008). Emits per-task
`{index, scenario_id, category, difficulty, kind, origin}` and asserts 42 unique ids
all present in the corpus. Output:
```
wrote tasks_42.json : 42 tasks (34 canonical + 8 variants; 19 real / 23 synthetic)
```

**2. Task file (`tasks_42.json`).** 42 tasks. Difficulty spread 3/4/5 = 9/15/18
(real curriculum signal). Carries provenance so a downstream train/eval split is auditable.

**3. Config (`train_rft_42.yaml`).** GRPO over `hud_env_v2.py` (deterministic-judge reward)
on `tasks: all` (the 42), `group: 6`, `steps: 30`, `lr: 1e-5`, `reset_head: true`,
`curriculum: true`, plus a `smoke:` block (2 tasks / group 4 / 1 step) for fail-fast.

**4. Launcher (`train_rft_42.py`).** The key difference from the stock `train_rft_v2.py`:
it does NOT index into `Taskset.from_module` (which enumerates only the 34 canonical ids
and cannot reach the 8 variants). Instead it imports `hud_env_v2.investigate_v2` and
constructs `investigate_v2(scenario_id=s)` for each of the 42 explicit ids. Supports
`--dry-run` (offline corpus validation, no `hud` import) and `--smoke` (live).

## Relationship to core files (NOT modified)
- Imports `hud_env_v2.investigate_v2` and `hud_env.SCENARIOS` — read-only, additive.
- Reuses the existing deterministic reward (`hud_env_v2._grade_v2` -> `rex.scoring.mechanism_score`).
- The stock 10-task runner (`train_rft_v2.py`) is left untouched; D14 is a parallel,
  task-namespaced launcher. No proposed patch to a core file was necessary because the
  42-set is expressible additively.

## How to run (documented in the YAML header too)
```
cd experiments/ralph_outputs/D14/artifacts
python3 assemble_tasks.py                                      # (re)build tasks_42.json
python3 train_rft_42.py --config train_rft_42.yaml --dry-run   # offline validation
set -a; source ~/.zshrc; set +a
../../../../.venv-hud/bin/hud models fork Qwen/Qwen3-8B --name opensre-qwen3-8b   # once
../../../../.venv-hud/bin/python train_rft_42.py --config train_rft_42.yaml --smoke
../../../../.venv-hud/bin/python train_rft_42.py --config train_rft_42.yaml       # full run
```
