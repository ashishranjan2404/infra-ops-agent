# F3 — Test Results

All commands run from `/Users/mei/rl`, Python 3.13.

## T1 — validator passes on the authored deliverable
```
$ python3 experiments/ralph_outputs/F3/artifacts/validate_conclusion.py
ALL CHECKS PASSED (7 check groups; 929 words)
exit=0
```
PASS. Structure (6 ordered headings), content contract (framing phrase, ≥4 named artifacts,
all reward coefficients, ceiling tokens, revocation-honesty clause, no placeholders), and all
9 provenance rows verified against source files.

## T2 — negative control: remove a required heading
Replaced `## The evidence` with `## (removed)` in a temp-mutated copy, ran validator, restored.
```
exit: 1
FAILED (1 issue(s)):
  - structure: missing/out-of-order heading: evidence subsection
```
PASS (correctly fails). File restored and re-verified passing afterward.

## T3 — negative control: bogus provenance value
Appended a row `bogus claim / 9.99nonexistent / ARCHITECTURE.md:1`, ran, restored.
```
exit: 1
FAILED (1 issue(s)):
  - provenance row 11: value '9.99nonexistent' not in ARCHITECTURE.md
```
PASS (correctly fails). File restored.

## Fix applied during testing
First T1 run FAILED on provenance row 2: the reward formula was attributed to `README.md:75`,
but `README.md:75` is unrelated prose — the formula lives at `ARCHITECTURE.md:75`. Corrected
the `source` column in `claims_provenance.tsv`; re-ran T1 → PASS. This is exactly the drift the
provenance check exists to catch.

## Markdown sanity
```
$ grep -c '^#' CONCLUSION.md   -> 6   (1 H1 + 5 H2, balanced)
$ wc -w < CONCLUSION.md        -> 929 (> 700 floor)
```
PASS.

## Net
3/3 test cases behave as specified; the one real defect (mis-cited source line) was caught by
the harness and fixed.
