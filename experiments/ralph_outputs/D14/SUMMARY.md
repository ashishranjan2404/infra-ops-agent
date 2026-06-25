# D14 — Summary

**Task:** Run RFT on the 42-incident benchmark (was only 10 tasks). Build a training config
using all 42 incidents as the RFT task set + the dataset-assembly script. Compute cap ~15 min.

## Delivered (real, validated)
- `artifacts/assemble_tasks.py` — deterministic dataset assembler: opensre corpus (319 recs)
  -> 42 incidents = 34 canonical (15 synthetic + 19 real postmortems) + 8 hard variants.
- `artifacts/tasks_42.json` — the assembled 42-incident task file (provenance per task:
  category, difficulty 3/4/5, kind, origin). 42 unique ids, all verified in corpus.
- `artifacts/train_rft_42.yaml` — the runnable GRPO config over `hud_env_v2.py`
  (deterministic-judge reward), `tasks: all`, curriculum easy->hard, reset_head, smoke block.
- `artifacts/train_rft_42.py` — config-driven launcher building the Taskset from explicit
  scenario_ids (the stock index-based runner can only reach 34 canonical ids; 8 variants
  are index-invisible). `--dry-run` (offline) + `--smoke`/full (live).
- `artifacts/smoke_run.jsonl` — real live-smoke reward log (mean 0.6586, spread 0.0562).

## Verification
py_compile + yaml parse OK; dry-run resolves all 42 ids (missing=[]); live smoke through
`.venv-hud` executed rollouts -> deterministic reward -> forward/backward step end-to-end.

## "10 -> 42" proven
Stock runner default = 10 index-selected tasks; D14 = 42 explicit-id tasks incl. 8 variants
unreachable by index (live smoke instantiated `001-oom_kill-s019` etc.).

## Blocker (honest)
A converged 42xgroupx30-step run wasn't completed: exceeds the ~15-min compute cap, and a
re-run hit a transient 409 (shared trainable head held by another concurrent worker). The
config + task file + launcher + proven smoke are complete; the long run is the documented
compute-capped follow-on. The placeholder model slug `opensre-qwen3-8b` must be
`hud models fork`-ed before a real run (404 on resolve otherwise).

## Core files: untouched
Only additive imports of `hud_env_v2`/`hud_env`; `train_rft_v2.py` and all `rex/sim/agent`
core left unmodified.
