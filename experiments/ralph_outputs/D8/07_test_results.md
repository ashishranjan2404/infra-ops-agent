# D8 — 07 Test Results

## Unit test (real output)
```
$ python3 -m pytest experiments/ralph_outputs/D8/artifacts/test_fireball_adapter.py -v
platform darwin -- Python 3.13.7, pytest-9.0.2
collected 11 items
test_fixture_loads PASSED
test_record_with_no_command_is_skipped PASSED
test_record_with_no_state_is_skipped PASSED
test_non_dict_is_skipped PASSED
test_basic_shape PASSED
test_state_change_detected PASSED
test_no_state_change_lower_reward PASSED
test_fireball_multitarget_renders_all_actors PASSED
test_stream_filters_unusable PASSED
test_convert_file_roundtrip PASSED
test_malformed_line_skipped PASSED
============================== 11 passed in 0.02s ==============================
```
**Result: 11/11 PASS.**

## One fix applied during testing
- First run: `test_no_state_change_lower_reward` failed with `IndexError` because
  the matcher used `.endswith("AC too high)")` but the fixture string ends with a
  trailing period (`"... miss (AC too high)."`). Fixed the matcher to
  `"AC too high" in ...`. Re-ran: green. (Test-only fix; adapter unchanged.)

## Adapter compile check
```
$ python3 -m py_compile fireball_adapter.py   -> adapter compiles
```

## Converter end-to-end (real output)
```
$ python3 fireball_adapter.py --in fireball_fixture.jsonl --out fireball_train.jsonl
{"records_in": 7, "examples_out": 6, "skipped": 1}
$ wc -l fireball_train.jsonl  -> 6
```
The 1 skipped record is `syn-combat-004` turn 1 (empty `commands` -> not a
transition), exactly as designed. Every output line parsed as valid
training-format json (asserted in `test_convert_file_roundtrip`).

## Config parse check
```
$ python3 -c "import yaml; yaml.safe_load(open('fireball_sft.config.yaml'))"  -> yaml ok
```

## NOT run (blocked)
- Actual SFT training on Fireball.
- The Claim-2 transfer eval (cascade vs simple, pass@1/2/5).
Both require the real FIREBALL corpus, which is **not in the repo (pending from
Wenji)**. Per the brief, no results were fabricated. Running the config against
the synthetic fixture would only smoke-test plumbing and is explicitly guarded
against being treated as a real run (`is_real_fireball: false`).
