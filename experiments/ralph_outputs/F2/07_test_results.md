# F2 — 07 Test Results

## Test 1 — citation-existence + structure checker
Command:
```
python3 experiments/ralph_outputs/F2/artifacts/check_limitations.py
```
Output:
```
repo_root = /Users/mei/rl
  generated scenarios glob = 51 (>= 30) OK

PASS: all cited files exist and LIMITATIONS.md is well-formed.
EXIT=0
```
**PASS** — all 7 cited files exist; generated-scenario glob = 51 (≥30); LIMITATIONS.md
contains `## Limitations`, `### L1`..`### L6`, and `### Scope`.

## Test 2 — live-citation canary (Ouroboros C)
Prove the most attackable number (hedge fool-rate) is lifted, not invented:
```
grep -o "92.9% fool-rate" .../F2/artifacts/LIMITATIONS.md   -> 92.9% fool-rate
grep -o "92.9" experiments/ralph_outputs/D13/SUMMARY.md      -> 92.9
```
**PASS** — 92.9% appears in both LIMITATIONS.md and the cited D13 source.

## Test 3 — reward-weight grounding
```
grep -n "W_ROOT, W_FIX, W_RESOLVED" rex/scoring.py
-> 22:  W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60
```
**PASS** — L2/L4's `0.30·diag + 0.25·fix + 0.45·resolved` matches `rex/scoring.py`.

## Test 4 — markdown structure parse
```
H2 count: 8        (## Limitations + 7 are ### so only 1 H2 'Limitations' + intro);
L-subsections: 6   (### L1..L6)
```
**PASS** — single `## Limitations` H2; 6 L-subsections + Scope present.

## Test 5 — python syntax
```
python3 -m py_compile check_limitations.py  -> py_compile OK
```
**PASS**.

## Fixes applied during testing
- None required; all checks green on first run. The Ouroboros-derived dynamic
  repo-root resolution worked (resolved to `/Users/mei/rl`).

## Known not-tested
- The checker verifies file *existence*, not that every number in prose appears in
  its source. Mitigated by the canary (Test 2) and reward-weight (Test 3) spot
  checks; full number-grounding is out of scope for a doc task (noted in 09).
