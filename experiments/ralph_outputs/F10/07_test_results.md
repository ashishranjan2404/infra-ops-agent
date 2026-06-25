# F10 — 07 Test Results

## T1 — validator on the real sheet
```
$ python3 check_signoff.py signoff_sheet.md
=== Sign-off tally ===
  cleared  : 0  []
  partial  : 0  []
  rejected : 0  []
  pending  : 9  ['C1', 'C2', 'C3', 'S1', 'S2', 'S3', 'S4', 'N1', 'N2']
  malformed: 0  []
  TOTAL claims: 9
=== Evidence pointers ===
  present in repo : 4
    OK   experiments/CLAIMS_EVIDENCE.md
    OK   rex/runs/ablation.json
    OK   rex/runs/frontier.json
    OK   rex/runs/harness_synth_v2.json
SUMMARY: 0 cleared, 9 not-yet-cleared, 0 malformed.
EXIT=0
```
**PASS.** All 9 claims parsed (3 primary + 4 supporting + 2 negative), all PENDING,
0 malformed. All 4 in-repo evidence files resolve on disk.

## T2 — synthetic sheet, one fully-APPROVED row
```
  cleared  : 1  ['C1']
  partial  : 1  ['C2']
```
**PASS.** Fully-approved row → cleared; mixed row → partial.

## T3 — synthetic sheet with a REJECTED cell
```
  rejected : 1  ['C1']
```
**PASS.** Any REJECTED cell dominates the row classification.

## T4 — synthetic sheet with a missing author cell
```
  malformed: 1  ['C1']
Sheet has malformed rows.
real exit code=1
```
**PASS.** Missing author cell → malformed → exit 1 (the one error path).

## T5 — compile check
```
$ python3 -m py_compile check_signoff.py
compile OK
```
**PASS.**

## Evidence-reality spot check
```
$ ls -la rex/runs/harness_synth_v2.json rex/runs/ablation.json rex/runs/frontier.json
-rw-r--r-- 4147  rex/runs/ablation.json
-rw-r--r-- 2997  rex/runs/frontier.json
-rw-r--r-- 3100  rex/runs/harness_synth_v2.json
```
All cited primary-evidence files are real and non-empty.

## Fixes applied during testing
- None required. Parser handled alignment colons, optional outer pipes, and
  per-table column re-indexing on first run. The C2 external-evidence case is handled
  by `EXTERNAL_EVIDENCE` keyword matching (no false "MISSING" reported).

## Summary
5/5 tests pass. The deliverable sheet parses to the expected `9 pending` state and the
validator's error path (malformed → exit 1) works.
