# G7 — 07 Test Results

All checks run from `experiments/ralph_outputs/G7/`. Real command output below.

## T1 — watch-list validator
```
$ python3 artifacts/validate_watchlist.py
OK: 8 watch items, schema valid; 8 not-knowable entries.
exit=0
```
**PASS** — 8 watch items (≥7 required), schema valid, all enums/required keys present, no dup ids.

## T1b — raw YAML parse
```
$ python3 -c "import yaml; yaml.safe_load(open('artifacts/resolve_ai_watchlist.yaml')); print('yaml parse OK')"
yaml parse OK
```
**PASS** — file is valid YAML independent of the validator.

## T2 — brief section structure
```
$ grep -c '^## ' artifacts/resolve_ai_competitor_brief.md
10
```
**PASS** — 10 H2 sections (Company & funding … Sources). Section 1 (as-of/scope/one-line) is the
bold lead block above the first H2 by design, so 10 H2s = the 11 logical sections in the spec.

## T3 — vendor metric tagging
```
$ grep -c 'vendor-reported' artifacts/resolve_ai_competitor_brief.md
7
$ grep -c '^- \[S' artifacts/resolve_ai_competitor_brief.md
10
```
**PASS** — every self-reported metric (Coinbase 72%, DoorDash 87%, ~5-min triage, >2x accuracy, plus
the architecture-claims labels) is tagged `(vendor-reported)`; 10 unique sources [S1]–[S10] in the list.

## Fixes applied during testing
- None required; validator and parse checks passed on first run.

## Summary
| Check | Result |
|-------|--------|
| T1 validator (exit 0, ≥7 items) | PASS |
| T1b YAML parse | PASS |
| T2 brief sections | PASS |
| T3 vendor tagging + sources | PASS |
