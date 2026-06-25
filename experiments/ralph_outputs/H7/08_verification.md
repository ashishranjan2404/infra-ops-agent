# 08 — Verification against success criteria

| Criterion (from 01) | Met? | Evidence |
|---|---|---|
| JSON parses | YES | `json.load` OK, 11 models (07) |
| Every real ROSTER model present | YES | 8 eval rows = exact `agent/models.py` ROSTER keys; test_known_real_references_present passes |
| Every forked Qwen slug present | YES | opensre-qwen3-8b / -v2 / -30b rows, slug `...-1e439a` + 30B; from train scripts + MEMORY |
| CLI list/filter/show/query/stats work | YES | live runs in 06/07; all exit 0 |
| Missing id -> exit 2 | YES | `show does-not-exist` -> 2 (test passes) |
| Tests pass | YES | 5/5 direct + 5/5 pytest |
| No shared core file edited | YES | only new files under artifacts/; `git status` confirms (09) |

## Are the outputs real, not placeholder?
Yes. Every numeric value is traceable:
- Frontier means (opus 0.81→0.86, haiku/gpt 0.63→0.86, gemini 0.75→0.86, deepseek 0.81→0.86)
  are copied verbatim from `rex/runs/frontier.json` (verified by re-reading that file).
- Training start/end mean rewards are the first/last step of the actual jsonl run logs
  (`train_qwen3-8b.jsonl`: 0.522→0.491; `_v2`: 0.5039→0.541; `30b`: 0.4737→0.4905).
- Slugs and the "can't GRPO closed models" framing come from `opensre-traj/train_rft*.py`
  and MEMORY `rft-training-run.md`.

## Honest gaps (not hidden)
- `eval_pass_at_1` is null for all 11 rows — no per-model pass@1 exists in repo result files
  for these exact ids, so it is honestly null rather than fabricated.
- Registry numbers are a verified snapshot, not auto-derived (drift risk — see 09).
