# B15 — 07 Test Results

## 1. Script compiles
```
$ python3 -m py_compile gen_comparison.py
OK
```

## 2. JSON parse-checks
```
$ python3 -c "import json; json.load(open('sregym_reported.json'))"
sregym json OK
```

## 3. `--selftest` (6 asserts)
```
$ python3 gen_comparison.py --selftest
selftest OK   (exit 0)
```
Asserts covered: `fmt_pct` formatting (incl. None→"—"), SREGym `n_problems==90` &
8 leaderboard rows, our A1 `rex` overall pass@1 ≈ 0.897 (got 0.8968), exactly 5 conditions
parsed, per-family populated (regression guard for `by_family` nesting), novel `rex` == 1.0.

## 4. Full render run
```
$ python3 gen_comparison.py    (exit 0)
[wrote .../comparison_table.md and .../our_pass_at_1.json]
```

## 5. Generated-output sanity
```
A1 conds: ['zero_shot','best_of_n','retry_realistic','rex_no_oracle','rex']
A2 conds: ['zero_shot','best_of_n','retry_realistic','rex_no_oracle','rex']
rex A1 overall p1: 0.8968
source_runs models: glm-5p2 (A1), deepseek-v4-pro (A2)
```

## Bug found & fixed during testing
- **Per-family columns rendered "—".** Root cause: A1's schema nests per-family stats under
  `by_condition[cond]["by_family"][family]`, not `by_condition[cond][family]`. The first render
  produced empty Table 2. **Fix:** `_cond_block` now looks in `by_family` first
  (falling back to a flat key for robustness). Added a selftest assert
  (`rex.novel.p1 == 1.0`) so the regression can't recur silently. Re-ran → Table 2 populated
  (simple 88.9 / cascade 85.0 / novel 100.0% for rex).

## Cross-check against source artifacts (numbers are real, not invented)
- A1 `rex` overall pass@1 in `full_pass_at_k_glm-5p2.json` = 0.8968 → matches table 89.7%.
- A1 `zero_shot` overall = 0.2302 → 23.0%. A2 `rex` overall = 0.8933 → 89.3%. All trace to disk.
- SREGym Claude Code no-noise E2E = 0.607 → matches paper/leaderboard (60.7%).

## Status: PASS — script runs clean, all asserts green, outputs trace to real artifacts.
