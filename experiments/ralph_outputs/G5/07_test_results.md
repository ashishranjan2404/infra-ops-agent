# G5 — 07 Test Results

## Validator — main run
```
$ cd experiments/ralph_outputs/G5/artifacts && python3 validate_matrix.py
VALIDATION PASSED: 5 dimensions x 4 columns, all cells cited, all tags resolve, both vendor
columns carry a 'vendor-stated' flag.
EXIT=0
```

## Validator — selftest (T1..T4)
```
$ python3 validate_matrix.py --selftest
selftest:
  [PASS] T1 happy path -> clean: errors=[]
  [PASS] T2 missing tag -> fail: errors=['cell [Open benchmark / us] has no [Sn] citation']
  [PASS] T3 unresolved tag -> fail: errors=['unresolved tag S99 in [Open benchmark / us]', ...]
  [PASS] T4 source missing url -> fail: errors=["source S1 missing/empty field 'url'"]
EXIT=0
```
All four fixtures behave as specified: the happy path passes; a missing tag, an unresolved tag,
and a source without a url each fail loudly with a precise message.

## sources.json parse check
```
$ python3 -c "import json;json.load(open('sources.json'));print('sources.json OK')"
sources.json OK
```

## Markdown sanity
- `positioning_matrix.md` table parses to exactly 5 dimension rows × 4 competitor columns
  (enforced by C1 in the validator, which passed).
- All 11 sources S1–S11 are referenced by the matrix and all referenced tags resolve (C2/C3).

## Fixes applied during testing
- Initial draft: the C5 vendor-flag check relied on a module-global `VENDOR_COLS_SEEN` that was
  not reset between selftest fixtures, causing T2/T3 to leak C5 state. Fixed by resetting
  `VENDOR_COLS_SEEN` at the start of each `run()` in `_selftest`. After the fix all four fixtures
  pass independently.

## Result
All tests pass. No fabricated benchmark numbers were produced — every competitor figure is a
real, dated, cited claim, with vendor marketing explicitly flagged as unverified.
