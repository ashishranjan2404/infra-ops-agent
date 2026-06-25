# F7 — 07 Test Results

## T1 — JSON parses
```
$ python3 -c "import json;d=json.load(open('.../attacks.json'));print('ok',len(d['attacks']),'attacks')"
ok 10 attacks
```
PASS.

## T2 — Validator (schema + theme coverage + doc structure + substance)
First run surfaced **two real bugs** (good — the test did its job):

1. All 50 label checks failed: regex `\*\*Steelman\*\*` didn't match the doc's `**Steelman.**`
   (period inside the bold). → Fix: tolerant matcher `\*\*Steelman[.:]?\*\*`, case-insensitive.

2. After fix #1, one remaining failure:
   ```
   - A4: Steelman body too short (100 chars)
   ```
   Not a doc defect — the substance gate stopped at an *inline* bold (`**0.522 → 0.491**`) inside
   A4's steelman, truncating the measured body. → Fix: extract body up to the next *known label*
   (`Steelman|Honest response|Probability|Depth|Closing evidence`), not any `**`.

Final run:
```
$ python3 experiments/ralph_outputs/F7/artifacts/validate_attacks.py
attacks: 10
mandatory themes present: True
PASS — deliverable structurally complete and substantive
EXIT=0
```
PASS.

## T3 — Negative control (theme-drop)
Removed `small_n` from an in-memory copy of the data; `check_themes` must report it.
```
missing after drop: ['small_n']
NEGATIVE CONTROL PASS
```
PASS — the theme check is not vacuous; it genuinely detects a missing mandatory weakness.

## T4 — Py-compile / syntax
```
$ python3 -m py_compile experiments/ralph_outputs/F7/artifacts/validate_attacks.py  → exit 0
```
(implied by successful import/run in T2/T3.)

## Summary
All tests pass after 2 fixes. The validator found real defects in its first run (label-format
brittleness and a body-extraction bug), both fixed; the negative control confirms the
theme-coverage check actually bites. Deliverable is structurally complete, substantive, and
covers all five mandated weakness themes.
