# E6 — 08 Verification

## Success criteria (from 01) — checked

| # | criterion | status | evidence |
|---|---|---|---|
| 1 | three pure deterministic transforms | ✅ | `fireball_ablate.py`; purity test `test_input_not_mutated` passes |
| 2 | state_only + action_only partition full exactly | ✅ | fixture 4+6=10; real 2327+2327=4654; `test_state_and_action_partition_trajectory` |
| 3 | unit tests pass | ✅ | 16/16, see 07 |
| 4 | harness runs on fixture AND real corpus | ✅ | both runs in 07, 319 records clean |
| 5 | blocker documented, no fabricated metrics | ✅ | `blocker` field in report; 0 metrics produced |

## Are outputs real (not placeholder)?
Yes.
- `fireball_ablate.py` — real, importable, 16 passing tests, runs via CLI.
- `fixture_fireball.jsonl` — real valid JSONL, schema-identical to opensre/FIREBALL records
  (verified by transforming it and by the real-corpus run using the same code path).
- `_variants_real/*.jsonl` — 3×319 real records derived from the actual in-repo corpus,
  re-parsed without error.
- `ablation_report*.json` — real generated reports.

## Determinism
Transforms use `copy.deepcopy` + key/role filtering only — no randomness, no time, no I/O
in the transform layer. Re-running produces byte-identical variant files.

## Honest scope statement
E6 delivers the **data-variant design + transforms + harness + tests** — the only new piece
the task owns. It does **not** deliver per-variant model accuracy; that step is blocked on
missing data (see 09). This matches the brief: "a correct scaffold + honest blocker beats
fabricated numbers." Deliverable is complete; downstream run is blocked.
