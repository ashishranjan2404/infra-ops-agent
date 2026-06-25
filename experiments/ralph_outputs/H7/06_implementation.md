# 06 — Implementation

## Artifacts created (all under experiments/ralph_outputs/H7/artifacts/)
1. **model_registry.json** — 11 real models, schema_version 1.0, self-documenting `fields`
   block, per-row `source` provenance, `notes` block. No shared core file touched.
2. **model_registry.py** — dependency-free CLI (stdlib only): `list`, `show`, `query`, `stats`,
   with `--role --status(csv) --provider --base --json` filters; id-or-slug lookup; exit codes.
3. **test_model_registry.py** — 5 tests, runnable directly or under pytest.

## What was populated (every value harvested from a real repo reference)
### Eval models (8) — from `agent/models.py:ROSTER`
- claude-opus-4-8, claude-haiku-4-5, gpt-5.5, gemini-3.1-pro, deepseek-v4-pro, grok-4.3,
  glm-5p2, minimax-m3. All `role=eval`, `training_status=frozen`.
- Frontier baseline/REx mean rewards for the 5 models present in `rex/runs/frontier.json`:
  opus 0.81→0.86, haiku 0.63→0.86, gpt-5.5 0.63→0.86, gemini 0.75→0.86, deepseek 0.81→0.86.
- grok-4.3 / glm-5p2 / minimax-m3 frontier fields = null (not in that run) — honest.
- claude-haiku-4-5 also flagged as the REx proposer (`rex/loop.py:_SMALL_MODEL`).

### Trainable models (3) — forked Qwen via HUD Tinker
- **opensre-qwen3-8b** (slug `opensre-qwen3-8b-1e439a`, base Qwen/Qwen3-8B): status `flat`,
  train mean reward 0.522 → 0.491 (went DOWN). Source: `opensre-traj/runs/train_qwen3-8b.jsonl`.
- **opensre-qwen3-8b-v2** (same fork, P4 RLVR v2 with deterministic judge + single-scenario
  GRPO groups): status `trained`, 0.5039 → 0.541 (slight up). Source: `train_qwen3-8b_v2.jsonl`.
- **opensre-qwen3-30b** (Qwen3-30B-A3B MoE): status `aborted`, 0.4737 → 0.4905, killed at
  step 13 by a Tinker awselb 503. Source: `train_qwen3-30b.jsonl` + `.log`.

## Key real references mined
- `agent/models.py` ROSTER (8 models, providers, anchors, no_temperature flags)
- `opensre-traj/train_rft.py` / `train_rft_v2.py` (fork command, "can't GRPO closed models")
- `opensre-traj/runs/train_*.jsonl` (per-step mean_reward — start/end extracted)
- `rex/runs/frontier.json` (baseline vs REx mean reward per model)
- `rex/eval_pass_at_k.py` (default --model glm-5p2; --frontier model set)
- `rex/loop.py` (_SMALL_MODEL = claude-haiku-4-5 proposer)
- MEMORY `rft-training-run.md` (forked slug `...-1e439a`, 30B aborted, Qwen3.5-4B 502s)

## Shared-file policy
No edits to `rex/*`, `sim/*`, `agent/*`, `experiments/*.py`, `ralph_status.json`. The registry
only READS those files; it copies verified facts into a new task-namespaced JSON.
