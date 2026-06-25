# F12 — 07 Test Results

Validation of `artifacts/SRE_Degrees_2pager.md` against the step-04 test cases. Real command
output below.

## Commands run
```
$ wc -w SRE_Degrees_2pager.md            -> 1135   (T1: in [1100,1400] PASS)
$ grep -ci problem  ...                  -> 3      (T2 PASS)
$ grep -ci insight  ...                  -> 2
$ grep -ci evidence ...                  -> 1
$ grep -ci market   ...                  -> 1
$ grep -ci ask      ...                  -> 2
$ grep -c 0.23 ; grep -c 0.90            -> 1 ; 1  (T3: headline pair present PASS)
$ grep -c 0.24 ; grep -c 0.89            -> 1 ; 1  (T4: 2nd-model corroboration PASS)
$ grep -ic "where the lift comes from|feedback content|vanish|baseline" -> 4 (T5 PASS)
$ grep -c McNemar ; grep -c deterministic ; grep -c seeds  -> 1 ; 1 ; 1 (T6 PASS)
$ grep -ciE "pass@k|Thompson|FIREBALL|MCTS|ouroboros|oracle" -> 0       (T7 jargon-clean PASS)
$ grep -c '^##'                          -> 8      (T8: section structure intact PASS)
```

## Results table
| Test | Check | Result |
|---|---|---|
| T1 | word count in [1100,1400] | PASS (1135) |
| T2 | all 5 topics present | PASS |
| T3 | headline 0.23 / 0.90 | PASS |
| T4 | 2nd model 0.24 / 0.89 | PASS |
| T5 | honest negative present | PASS |
| T6 | footnote rigor (n/seeds/McNemar/deterministic) | PASS |
| T7 | no undefined jargon | PASS |
| T8 | markdown structure (8 sections + footnote) | PASS |

## Evidence cross-check
Ran the claim→source mapping in `evidence_check.md` against A1/A2 files. Every quantitative
claim resolves to a real artifact field:
- 0.230 / 0.897 / 42 incidents / 630 episodes / disjoint CIs  ← A1 SUMMARY+result.json
- 0.240 / 0.893 / 750 episodes / McNemar p<0.0001 / rex_no_oracle 0.287  ← A2 SUMMARY+result.json
- reward weights / frozen LLM / two-tier sim  ← ARCHITECTURE.md
Forbidden-number audit (revenue/customers/precise TAM): none present → PASS.

## Fixes applied during testing
- First draft was 1056 words (below the 1100 floor). Added two honest, on-thesis sentences
  (the "which red thing is lying to you" framing in §1 and a "picks and shovels" clause in §6).
  Re-ran `wc -w` → 1135. No numbers changed; no claim added that isn't backed by a source.

All tests pass.
