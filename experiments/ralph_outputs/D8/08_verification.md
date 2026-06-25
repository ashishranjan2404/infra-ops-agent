# D8 — 08 Verification

## Against the success criteria (from 01/03)

| Criterion | Status | Evidence |
|---|---|---|
| Adapter converts fixture deterministically | ✅ | `{records_in:7, examples_out:6, skipped:1}`, stable across runs |
| Unit test green | ✅ | 11/11 pass (07) |
| Output is valid training-format jsonl | ✅ | `test_convert_file_roundtrip` parses every line; shape = messages+reward+meta |
| Config parses + self-documents blocker & guard | ✅ | `yaml ok`; `is_real_fireball:false`, `provenance.blocked_on`, `do_not_fabricate:true` |
| `reward` is a data-quality weight, not a game score | ✅ | docstring of `_reward_for` + config comment |
| No fabricated Fireball numbers | ✅ | nothing trained/eval'd; blocker stated in 06/07/09/SUMMARY/config |
| No shared-core edits | ✅ | all files under `experiments/ralph_outputs/D8/artifacts/` |
| Replication bar recorded | ✅ | config eval block + 03/09 (multi-seed + CI on cascade/simple split) |

## Are the outputs real (not placeholder)?
Yes. The adapter is a working transform that runs from the CLI; the fixture is
valid jsonl exercising every branch; the test actually executes and asserts on
real outputs; the generated `fireball_train.jsonl` contains 6 real,
schema-correct training examples. None of these are stubs.

## What is honestly NOT done (and correctly so)
- No Fireball-trained model exists.
- No pass@1/2/5 transfer numbers exist.
These are blocked on Wenji's data and were deliberately not faked. The deliverable
is the *scaffold to produce them the moment the data lands*, plus the honest
blocker. Per the brief, this counts as a completed deliverable with a noted
downstream blocker.
