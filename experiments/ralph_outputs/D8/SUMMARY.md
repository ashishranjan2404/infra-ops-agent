# D8 — SUMMARY: Train on Fireball data (Claim 2)

## Goal
Claim 2: fine-tuning on FIREBALL D&D `state -> action -> state'` trajectories
improves pass@1 on cascade/multi-hop SRE incidents (the interesting asymmetry:
better on cascade, slightly worse on simple) vs OpenSRE-trained agents.

## Status: COMPLETED deliverable, Claim-2 evidence BLOCKED on data
The real FIREBALL corpus is **not in the repo** — pending Wenji pushing it. Per
the brief, no Fireball training or transfer-eval results were fabricated. What I
delivered is the runnable ingest + config + test scaffold the data will plug into.

## Delivered artifacts (all in `experiments/ralph_outputs/D8/artifacts/`)
- `fireball_adapter.py` — FIREBALL record -> project training format. Defensive
  field reads; skips non-transitions; explicit STATE_BEFORE/ACTION->RESULT/
  STATE_AFTER messages; documented data-quality `reward` weight (NOT a game
  score); CLI `--in/--out`.
- `fireball_fixture.jsonl` — 7 synthetic (`syn-combat-*`) records covering hit,
  kill, multi-target fireball, miss (no state change), heal, no-command skip,
  buff/effect.
- `test_fireball_adapter.py` — 11 unit tests, **all pass**.
- `fireball_sft.config.yaml` — SFT + Claim-2 transfer eval (pass@1/2/5, cascade
  vs simple, 3 baselines), fail-closed guard (`is_real_fireball:false`,
  `min_examples_for_real_run:2000`), provenance/blocker block.
- `fireball_train.jsonl` — generated output (6 examples) demonstrating the transform.

## Validation (real)
- `pytest ... -> 11 passed`
- `fireball_adapter.py --in fixture --out train -> {records_in:7, examples_out:6, skipped:1}`
- `yaml.safe_load(config) -> ok`
- adapter `py_compile` -> ok

## Blocker
Real FIREBALL corpus missing (Wenji). Downstream blocked: actual SFT run + the
cascade/simple transfer eval. When the data lands: set `data.input` to it, flip
`is_real_fireball: true`, fork the open model, run the config. Acceptance bar for
Claim-2 evidence (recorded, not met here): multi-seed + CI on a pre-registered
cascade-vs-simple incident split.

## Safety
No shared-core files edited; all artifacts are task-namespaced under D8.
