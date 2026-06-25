# D14 — 01 Plan

## Objective
Run RFT (GRPO) on the **full 42-incident benchmark** instead of the current 10-task
slice. Deliver (a) a runnable training config that uses all 42 incidents as the RFT
task set, and (b) the dataset-assembly script + the assembled 42-incident task file.
Compute cap ~15 min: if the open-model training backend is unavailable, deliver the
runnable scaffold + an honest backend blocker.

## Context discovered
- The opensre incident env (`opensre-traj/hud_env_v2.py`) is the RFT environment: a
  one-shot incident-diagnosis task with a **deterministic** reward (category 0.35 |
  P0 mechanism judge 0.20 | evidence kw 0.25 | ruled-out 0.10 | remediation 0.10).
- Tasks come from the corpus `opensre-traj/out/trajectories.jsonl` (319 records):
  **34 canonical incidents** (15 synthetic seed classes `001-015` + 19 real
  postmortem-derived `101-119`) + 285 perturbed variants (`-sNNN`).
- `hud_env_v2` exposes one task per *canonical* id (`canonical_ids()` -> 34 tasks).
- The existing runner `train_rft_v2.py` trains on a 0-based **index slice** into those
  34 tasks, defaulting to the first **10** (`--tasks 0..9`). That is the "currently
  only 10 tasks".
- Closed models (Claude/GPT/Gemini) are eval baselines only — GRPO needs an open,
  forkable trainable head (Qwen via the HUD Tinker provider).

## Why 42 (not 34)
The benchmark surface is 34 *canonical* incidents. To deliver a genuine 42-task RFT set
I take all 34 canonical incidents + 8 held-out **hard variants** (the most-perturbed
`-sNNN` variant of 8 distinct synthetic bases). This (1) hits exactly 42, (2) adds
within-class diversity the canonical-only set lacks, and (3) uses only REAL corpus keys.

## Approach
1. `assemble_tasks.py` — read the corpus, select the 42 ids deterministically, emit
   `tasks_42.json` (scenario_id + category + difficulty + kind + origin per task).
2. `train_rft_42.yaml` — runnable GRPO config (model, env, task_file, group, steps, lr,
   reset_head, curriculum, out) + a `smoke:` override block.
3. `train_rft_42.py` — config-driven launcher that builds the Taskset from **explicit
   scenario_ids** (NOT integer indices — 8 of the 42 are variants unreachable by index)
   using the existing `hud_env_v2.investigate_v2` template. Additive; touches no core file.
4. Validate: py_compile, YAML parse, `--dry-run` (offline corpus-id resolution + curriculum
   order), then a real `--smoke` run through `.venv-hud`.

## Files to create (all task-namespaced)
- `experiments/ralph_outputs/D14/artifacts/assemble_tasks.py`
- `experiments/ralph_outputs/D14/artifacts/tasks_42.json`
- `experiments/ralph_outputs/D14/artifacts/train_rft_42.yaml`
- `experiments/ralph_outputs/D14/artifacts/train_rft_42.py`

## Files NOT modified (shared core — per brief)
`opensre-traj/hud_env*.py`, `opensre-traj/train_rft*.py`, `rex/*`, `sim/*`, the corpus.

## Dependencies
`pyyaml` (in requirements-rex.txt), and for the live run: `.venv-hud` (3.12) + `HUD_API_KEY`
+ a forked trainable Qwen slug (`hud models fork Qwen/Qwen3-8B --name opensre-qwen3-8b`).

## Risks
- The forked model slug may not exist under this account -> 404 on resolve (a config/ops
  blocker, not a code blocker).
- Corpus `difficulty` field name (not `scenario_difficulty`) — must read the right key
  for the curriculum to be real.
- Running 42 tasks x group x steps within 15 min wall-clock is not feasible; smoke proves
  the pipeline, full run is the documented compute-capped step.

## Success criteria
- `tasks_42.json` has exactly 42 unique scenario_ids, all resolving in the corpus.
- The config + launcher parse and `--dry-run` clean (42 tasks, curriculum ordered).
- A real `--smoke` executes rollouts -> deterministic reward -> forward/backward step.
