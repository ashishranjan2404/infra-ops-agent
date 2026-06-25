# G3 — 07 Test Results

All commands run from `/Users/mei/rl/experiments/ralph_outputs/` with Python 3.13.7.

## 1. Python compile
```
$ python3 -m py_compile G3/artifacts/rank_leaderboard.py
compile OK
```
PASS.

## 2. JSON validity (cited SREGym data)
```
$ python3 -c "import json; json.load(open('G3/artifacts/sregym_reported.json')); print('json OK')"
json OK
```
PASS.

## 3. Script selftest (data integrity + invariants)
```
$ python3 G3/artifacts/rank_leaderboard.py --selftest
SELFTEST OK: 13 ranked rows; fair-best=0.349 rex=0.897 sregym_top=0.607
```
PASS — 6 assertions: n_problems==90, >=8 leaderboard rows, A1 numbers present, ranks form
a 1..N permutation, rows sorted desc by pass@1, REx present & out-of-regime, and
max(fair OURS) < max(SREGym e2e).

## 4. Full render (exit code + output)
```
$ python3 G3/artifacts/rank_leaderboard.py ; echo rc=$?
... (13-row ranked table + honest positioning) ...
[wrote .../ranked_leaderboard.md]
rc=0
```
PASS. Produced the real 13-row ranked table; fair band (retry/best_of_n) at rank 8,
REx at nominal rank 1 tagged `[OUT-OF-REGIME]`.

## 5. Markdown parse-check (reports)
```
positioning_report.md OK 5819 bytes
ranked_leaderboard.md OK 2866 bytes
```
PASS — both start with `#` and contain a markdown table.

## Fixes applied during testing
- Initial positioning text said our fair band sat "below SREGym's entire E2E band."
  The actual data shows 34.9% is ABOVE the two weakest Kimi-K2.5 rows (32.9% / 30.4%).
  Corrected `render()` to compute `n_below` and state "rank 8, lower band, above only the
  2 weakest entries." Re-ran selftest + render: still passes, text now accurate.

## Not run (honest)
- No live SREGym execution (no cluster / no SREGym install — it is an external benchmark).
  Their numbers are cited+frozen, not reproduced. Documented as a blocker in 09.
