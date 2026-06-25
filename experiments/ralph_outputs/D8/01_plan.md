# D8 — 01 Plan: Train on Fireball data (Claim 2)

## Objective
Claim 2 (from `experiments/CLAIMS_EVIDENCE.md`): fine-tuning on FIREBALL D&D
trajectory data — structured `state_before -> action -> state_after` transitions
from a non-SRE domain — improves pass@1 on **cascade / multi-hop** SRE incidents,
outperforming OpenSRE-trained agents (and slightly underperforming on *simple*
incidents — the interesting asymmetry).

## Hard constraint / reality
The real FIREBALL corpus (Zhou et al., EMNLP 2022; HF `lara-martin/FIREBALL`) is
**NOT in this repo**. It is blocked on Wenji pushing the data. Per the brief:
do NOT fabricate Fireball training results. Deliver the runnable scaffold +
honest blocker instead.

## Scope (what D8 actually delivers)
1. A **data-ingest adapter**: FIREBALL record -> the project's existing
   trajectory training format (the `messages`+`reward`+`meta` shape consumed by
   `opensre-traj/train_rft*.py`).
2. A **training config** (`fireball_sft.config.yaml`) that wires SFT on the
   adapted data and the Claim-2 transfer eval (cascade vs simple, pass@1/2/5),
   with a guard that refuses a "real run" on fixture data.
3. A **tiny synthetic fixture** mimicking the published FIREBALL schema, plus a
   **unit test** exercising the adapter (skip rules, state-change detection,
   reward weighting, file roundtrip, malformed-line handling).
4. A **clearly documented blocker** (here, in 07, 09, SUMMARY).

## Files to create (all task-namespaced, no shared-core edits)
- `experiments/ralph_outputs/D8/artifacts/fireball_adapter.py`
- `experiments/ralph_outputs/D8/artifacts/fireball_fixture.jsonl`
- `experiments/ralph_outputs/D8/artifacts/test_fireball_adapter.py`
- `experiments/ralph_outputs/D8/artifacts/fireball_sft.config.yaml`
- (generated) `fireball_train.jsonl`

## Dependencies
- `python3` 3.13, `pytest`, `pyyaml` (already in requirements-rex.txt).
- Eval/training depends on HUD `.venv-hud` + a forked open model — that is the
  *downstream* step, gated behind the data blocker; not run here.

## Risks
- Schema drift: the real FIREBALL dump may differ from the assumed fields ->
  adapter reads each field defensively and skips load-bearing-missing records.
- "reward" overload: Fireball has no game score; the adapter's reward is a
  documented *data-quality* weight, not a task score. Must be explicit to avoid
  a reviewer mistaking it for a Fireball outcome.
- Transfer claim is unverifiable until data lands — must not be asserted.

## Success criteria
- Adapter converts the fixture deterministically; unit test green.
- Config parses and self-documents the blocker + the no-fabrication guard.
- Output jsonl is valid training-format consumable by the existing trainer shape.
- Blocker documented honestly; zero fabricated Fireball numbers.
