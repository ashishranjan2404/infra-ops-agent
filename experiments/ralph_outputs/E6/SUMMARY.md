# E6 — SUMMARY

**Task:** Ablate Fireball: full trajectories vs state-only vs action-only.

## What got done
Designed and built the three ablation data variants as pure deterministic transforms
over the FIREBALL/opensre trajectory format (the E2/SCHEMA.md state_before->fix->state_after
shape), plus an ablation harness, a synthetic fixture, and a 16-test pytest suite.

- full — control (everything).
- state_only — keep tool results / evidence / state_before-after / recovery_check;
  drop the agent's thoughts, tool calls, and gold action sequence.
- action_only — keep the agent's thoughts + tool calls + canonical fix; drop all
  observed tool results / evidence / state numbers.

The two ablations partition the trajectory exactly (state_only + action_only step counts
== full), enforced by a unit test.

## Artifacts (experiments/ralph_outputs/E6/artifacts/)
- fireball_ablate.py — transforms + CLI (the new piece).
- fixture_fireball.jsonl — 2-record schema-identical synthetic fixture.
- test_fireball_ablate.py — 16 unit tests, all passing.
- run_ablation_e6.py — harness: emit 3 variants + structural report + blocker.
- _variants/, _variants_real/, ablation_report*.json — emitted outputs.

## Validation
- 16/16 unit tests pass.
- Harness runs on the fixture AND the 319-record in-repo opensre corpus (perfect
  partition: 2327 assistant + 2327 tool = 4654 steps).

## Blocker (documented, not faked)
Per-variant model training + eval is blocked: the real FIREBALL D&D corpus and a
fireball-trained slug are not in the repo (E2 / P7_fireball_status.md). Zero model
metrics fabricated. Downstream wiring (variant -> SFT/GRPO -> rex.eval_pass_at_k +
rex.scoring on cascades) is ready; only the data/slug are missing. action_only has
no state_after, so it is SFT-only (no computable reward).

## Shared-core safety
No edits to any shared core file. All outputs under E6/; the in-repo corpus was read-only.

Status: completed (deliverable real + tested; downstream run blocked on missing data).
