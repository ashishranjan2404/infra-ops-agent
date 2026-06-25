# 07 — Test Results

## pytest (synthetic fixture)
```
$ python3 -m pytest test_fireball_convert.py -v
test_fireball_convert.py::test_fixture_rows_validate PASSED              [ 14%]
test_fireball_convert.py::test_convert_basic_fields PASSED               [ 28%]
test_fireball_convert.py::test_multi_command_tool_verbs PASSED           [ 42%]
test_fireball_convert.py::test_trace_id_deterministic_and_unique PASSED  [ 57%]
test_fireball_convert.py::test_skip_empty_target PASSED                  [ 71%]
test_fireball_convert.py::test_invalid_row_raises PASSED                 [ 85%]
test_fireball_convert.py::test_output_json_serializable PASSED           [100%]
============================== 7 passed in 0.01s ===============================
```
Self-running fallback (`python3 test_fireball_convert.py`): `ALL 7 TESTS PASSED`.

## Real fetch (HuggingFace, live)
- `HfApi().dataset_info('lara-martin/FIREBALL')` → private=False, gated=None,
  license tag `cc-by-4.0`, `arxiv:2305.01528`, `size_categories:100K<n<1M`.
- `list_shards` → **1471** `filtered/*.jsonl` shards (1475 files incl. loader/README).
- `hf_hub_download` of `00068c6b03adc2c102756053cf6edd05.jsonl` → 1.7 MB, 111 rows.
- Captured real schema (17 keys) → `fireball_schema.py`.

## Converter on REAL data
```
$ python3 fireball_convert.py <real_shard>.jsonl -o /tmp/e2_real.jsonl
wrote 49 trajectory records -> /tmp/e2_real.jsonl
records: 49
all have target: True
all serializable: True
```
111 raw turns → 49 usable records (62 dropped: empty action or empty target,
the documented skip filter). Example real-derived record: action
`['!cast blink -t Amity']`, tools `['cast']`, result `"Amity Faust casts Blink!"`,
target `"*Entering the building, Amity moves forward..."`.

## Converter on synthetic fixture
```
$ python3 fireball_convert.py fireball_fixture.jsonl -o /tmp/e2_traj.jsonl
wrote 2 trajectory records   # row 3 skipped (empty after_utterances)
```

## Fixes applied during dev
None required — first run of pytest passed; converter ran clean on both fixture
and the real shard. (The skip-empty count 111→49 confirmed the filter behaves.)

## Pass/Fail
PASS — fetch succeeded (real, not faked), schema documented from real data,
converter validated on BOTH synthetic fixture and real shard, all tests green.
