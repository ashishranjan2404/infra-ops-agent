# B4 — Test Results

All commands run real; outputs pasted verbatim.

## Build runs
```
$ python3 experiments/ralph_outputs/B4/artifacts/classify_incidents.py
classified 51 incidents -> {'simple': 11, 'cascade': 20, 'novel': 20}
by source tier: {'registry': 32, 'real-outage': 10, 'mechanics': 3, 'name-rule': 6}

$ python3 experiments/ralph_outputs/B4/artifacts/stratify_pass_at_k.py
headline results: ['full_pass_at_k_glm-5p2.json', 'ablation_pass_at_k_deepseek-v4-pro.json']
partial (provisional): ['ablation_pass_at_k_glm-5p2.json.partial']
  simple: 10 table rows, 3 classified-but-unevaluated
  cascade: 10 table rows, 6 classified-but-unevaluated
  novel: 10 table rows, 10 classified-but-unevaluated
classifier-vs-result mismatches: 0
```

## Assertions

| ID | Check | Result |
|----|-------|--------|
| T1 | 51 yaml in → 51 unique rows out | PASS (files=51 rows=51 unique=51) |
| T2 | every type ∈ {simple,cascade,novel} | PASS (True) |
| T3 | registry incidents: classifier == registry family | PASS (0 mismatches) |
| T4 | registry-subset counts simple=8 cascade=14 novel=10 | PASS (Counter matches) |
| T5 | a11 `-leaf-`→simple (3), `-cascade-`→cascade (3) | PASS (both True) |
| T6 | every unregistered file labelled, tier∈{real-outage,mechanics,name-rule} | PASS (19/19) |
| T7 | 3 md tables produced, each ≥1 data row + type header | PASS |
| T8 | B4 numbers == A1 raw by_family numbers (parity) | PASS (105/105 exact, 0 bad) |
| T9 | consistency check runs; mismatches reported | PASS (0 mismatches, run cleanly) |

### T8 parity (exact-equality, glm-5p2 full run)
```
parity checks ok=105 bad=0
```
105 = 5 conditions × 3 types × 7 metrics (n, passes, pass@1, pass@2, pass@5, mean_reward,
reward_std). Every B4 table cell equals A1's published `by_family` value bit-for-bit, confirming
the renderer does not drift from the canonical estimator.

## Static validation
```
$ python3 -m py_compile classify_incidents.py stratify_pass_at_k.py   -> PY COMPILE OK
$ json.load(incident_types.json, stratified_pass_at_k.json)           -> JSON VALID
```

## Fixes applied during build
- Join classifier↔registry on `basename(registry.path)` AND snake-cased id (ouroboros 1.1/1.2):
  registry keys are snake_case, files are kebab-case — without normalization the 32 labelled
  incidents would have fallen through to the mechanics rule. Verified T3=0 mismatches confirms
  the join is correct.
- `is_real_outage` guarded against "Synthetic…" sources containing a year (ouroboros 1.3).
