# E6 — 01 Plan

## Objective
Ablate the supervision channels in Fireball-format SRE trajectories: **full** vs
**state-only** vs **action-only**. The deliverable E6 owns is the *data-variant
design + transforms + harness + tests*, not model metrics (training/eval is blocked,
see below).

## Question the ablation answers
A FIREBALL trajectory carries two supervision channels interleaved:
- **actions** — the agent's `thought` + tool call (the policy demonstration).
- **states** — observed tool results / evidence + `state_before/after` (grounding).

- *state-only*: drop actions. Can a model learn from watching the world change?
- *action-only*: drop states. Can a model learn the action policy ungrounded?
- *full*: control.

## Format (from E2 converter / SCHEMA.md)
Per-record FIREBALL/opensre shape: top-level `trajectory` list of
`{role:"assistant", thought, action}` and `{role:"tool", name, result, evidence_ref}`
steps, plus `remediation` (`fix_tool`, `canonical_fix`, `state_before`, `state_after`,
`recovery_check`), `evidence`, `answer`. Mirrors FIREBALL `state_before -> fix -> state_after`.

## Files to create (all task-namespaced under E6/artifacts/)
- `fireball_ablate.py` — three pure transforms + CLI.
- `fixture_fireball.jsonl` — synthetic schema-identical fixture (2 records).
- `test_fireball_ablate.py` — pytest unit tests on the transforms.
- `run_ablation_e6.py` — harness: emit 3 variants + structural stats report.

## Dependencies
Python 3.13 stdlib + pytest. No live cluster, no network. Validated additionally
against the in-repo `opensre-traj/out/trajectories.jsonl` (319 records, same schema).

## Risks
- Real FIREBALL D&D corpus absent → cannot produce model metrics (BLOCKER, documented).
- Ambiguity: which remediation keys count as "state" vs "action" → fixed by explicit
  key partition in the spec.

## Success criteria
1. Three transforms, pure (no input mutation), deterministic.
2. state_only + action_only step counts partition full exactly.
3. Unit tests pass.
4. Harness runs on fixture AND the 319-record real corpus.
5. Blocker documented honestly; no fabricated metrics.

## Shared-core safety
No edits to `rex/*`, `sim/*`, `agent/*`, `experiments/*.py`. All new files live under
`experiments/ralph_outputs/E6/`.
