# H7 — Model Registry — SUMMARY

## Deliverable
A real, repo-grounded model registry + a dependency-free CLI to list/query it.

- `artifacts/model_registry.json` — 11 models, schema v1.0, per-row `source` provenance.
- `artifacts/model_registry.py` — stdlib CLI: `list`, `show`, `query`, `stats`
  (filters: `--role --status --provider --base --json`; id-or-slug lookup; exit codes).
- `artifacts/test_model_registry.py` — 5 tests, pass under bare runner and pytest.

## What's tracked (all from real repo references — nothing invented)
- **8 frozen eval models** = the exact `agent/models.py` ROSTER (Claude opus/haiku, gpt-5.5,
  gemini-3.1-pro, deepseek-v4-pro, grok-4.3, glm-5p2, minimax-m3), with frontier
  baseline/REx mean rewards from `rex/runs/frontier.json` where the run covered them.
- **3 forked/trainable Qwen models** via HUD Tinker, with real GRPO start->end mean reward:
  - opensre-qwen3-8b (slug `...-1e439a`): **flat**, 0.522 -> 0.491 (down)
  - opensre-qwen3-8b-v2 (P4 RLVR, det. judge): **trained**, 0.5039 -> 0.541 (up)
  - opensre-qwen3-30b (MoE): **aborted** at step 13 on a Tinker 503, 0.4737 -> 0.4905

## Honesty notes
`eval_pass_at_1` is null for all rows — no per-model pass@1 exists in repo result files for
these ids, so it is honestly null, not fabricated. Real per-model reward lives in separate
`frontier_*` columns to avoid conflating mean reward with accuracy.

## Verification
JSON parses; 5/5 tests pass (numeric assertions pin the real training figures); CLI runs
clean. No shared core file edited — only new task-namespaced files under H7.

Status: **completed**.
