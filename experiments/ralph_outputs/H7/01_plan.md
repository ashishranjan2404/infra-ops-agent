# 01 — Plan (H7: Model Registry)

## Objective
A real, repo-grounded model registry that tracks every model the SRE-Degrees project
references — both the frozen eval policies (the ROSTER) and the forked/trainable open
models (the GRPO/RFT runs) — plus a small CLI to list/query it by slug, base, provider,
training status, and (where measured) eval pass@1 / mean reward.

## Approach
1. Survey real model references: `agent/models.py` (ROSTER), `opensre-traj/*` (forked Qwen
   slugs + training run logs), `rex/*` (eval models, proposer model, frontier results).
2. Extract real numbers only: frontier baseline/REx means (`rex/runs/frontier.json`) and
   GRPO per-step mean reward (`opensre-traj/runs/train_*.jsonl`). Leave pass@1 null where
   nothing real exists — do NOT invent.
3. Emit `model_registry.json` (data) + `model_registry.py` (dependency-free CLI).
4. Tests + a real CLI run.

## Files to create (all task-namespaced, no shared edits)
- `artifacts/model_registry.json`
- `artifacts/model_registry.py`
- `artifacts/test_model_registry.py`

## Dependencies
Python 3.13 stdlib only (json, argparse, subprocess). No network, no HUD key needed.

## Risks
- Inventing slugs/numbers (the cardinal sin) → mitigated by a `source` field per row.
- pass@1 not actually measured per-model in the repo → represent honestly as null.

## Success criteria
- JSON parses; every real ROSTER model + every forked slug present.
- CLI runs: list / filter / show / query / stats all work; missing id → exit 2.
- Tests pass. No shared core file edited.
