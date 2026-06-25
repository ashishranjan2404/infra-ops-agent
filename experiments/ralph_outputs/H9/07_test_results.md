# H9 — 07 Test Results

## Command 1 — JSON parse check
```
$ python3 -c "import json; json.load(open('leaderboard.json')); print('json ok')"
json ok
```
PASS — `leaderboard.json` is valid JSON.

## Command 2 — full verification harness
```
$ python3 verify_leaderboard.py
127.0.0.1 - - [25/Jun/2026 01:18:26] "GET /leaderboard.html HTTP/1.1" 200 -
127.0.0.1 - - [25/Jun/2026 01:18:26] "GET /leaderboard.json HTTP/1.1" 200 -
[PASS] leaderboard.json parses
[PASS] has entries array
[PASS] entry rank 1 schema
[PASS] entry rank 1 pass@1 in [0,1]
... (ranks 2-9 schema + range)
[PASS] real number A1/REx (tree + oracle feedback)
[PASS] real number A1/zero_shot
[PASS] real number A2/REx (tree + oracle feedback)
[PASS] real number E3/OpenSRE-trained (GRPO)
[PASS] real number E3/zero_shot (base 8B)
[PASS] HTML fetches leaderboard.json
[PASS] HTML renders entries
[PASS] HTTP serves leaderboard.html (200)
[PASS] HTTP serves leaderboard.json and parses

29/29 checks passed
```
**PASS — 29/29.** Exit code 0.

## What each block proves
- **Schema (ranks 1-9):** every row has the required keys and `pass@1 ∈ [0,1]`.
- **Real-number anchors:** the 5 headline cells match the literal values in A1/A2/E3 JSONs to
  1e-3 — i.e. the board is populated with real numbers, not placeholders. If any number drifts
  from its source task, this test fails.
- **HTML references:** the page fetches `leaderboard.json` and builds rows from `data.entries`.
- **Live HTTP load:** the directory is served by a real `socketserver`; both the page and the
  JSON return HTTP 200 and the JSON parses to the same entry count the page expects. This is the
  direct proof of the task requirement "verify it loads the JSON."

## Fixes applied during dev
- None required: first full run of `verify_leaderboard.py` returned 29/29. (E3 `pass@5` was
  intentionally encoded as `null` up front, so the `fmtPct(null) -> "—"` path needed no fix.)
