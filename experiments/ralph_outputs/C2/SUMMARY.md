# C2 — SUMMARY: harness synthesis on cascade incidents only

**Question:** If AutoHarness-style rule synthesis runs on ONLY cascade incidents, does it
find different rules than the baseline (mixed leaf+cascade) run?

**Answer: Yes — a structurally different, narrower rule-set.**

## What I did
Built `artifacts/cascade_synth.py`, a task-namespaced wrapper that reuses ALL of
`rex/harness_synth.py`'s machinery (6-feature extraction, spec-derived labels, the
no-exec rule interpreter, the 2x-false-allow scoring, and `thompson_search`) and changes
only two inputs: a cascade-only incident split (14 train / 6 held-out, drawn from
`scenarios_by_family()['cascade']`, 20 incidents total) and the mutation model. No shared
core file was edited.

## Result (model gpt-5.5, budget 8, real run)
| | baseline mixed (10 rules) | cascade-only (2 rules) |
|---|---|---|
| features guarded | treats_forbidden_category, leak_active, at_replica_limit, rollback_without_deploy | treats_forbidden_category only (+ spurious scale_deployment blanket) |
| train acc / FA% | 0.861 / 0.324 | 0.939 / 0.000 |
| held-out acc / FA% (own family) | 0.872 / 0.385 | 0.83 / 0.476 |

- Cascade-only synthesis DROPS every leaf/node guard (leak, replica-limit,
  rollback-without-deploy) because those hazards never appear in cascade training data —
  unlearnable, no supervision. Verified: cascade TRAIN hazards = {treats_forbidden_category,
  trap_action} only.
- It KEEPS the canonical cascade guard treats_forbidden_category ("don't treat a ruled-out
  cause"), fixing all 71 train false-allows.
- It ADDS an over-general unconditional scale_deployment block (overfits: scaling the loud
  victim is usually a trap in cascades) -> 5 held-out false-blocks, incl. 2 correct fixes.

## Honest caveats / blockers
- Model confound: baseline used claude-haiku-4-5; this used gpt-5.5 (Anthropic 400s, out of
  credits). Hazard-coverage difference is split-driven (the real finding); rule count/wording
  is partly model-driven.
- deepseek no-op (real blocker, handled): first run with deepseek-v4-pro returned EMPTY
  completions, degenerating synthesis to the empty seed (score 0.395 flat). Diagnosed live
  and switched to gpt-5.5. gemini-3.1-pro likewise emitted no parseable JSON.
- n=1, slight negative held-out delta vs hand-written (0.83 vs 0.864) — reported, not spun.

## Artifacts
- artifacts/cascade_synth.py — runnable wrapper (parses, runs, exit 0)
- artifacts/cascade_synth.json — real run output (validated)
- artifacts/compare.md — full comparison + caveats
- artifacts/run_gpt55.log, artifacts/run_deepseek_noop.log — captured evidence
- 01..10 step files
