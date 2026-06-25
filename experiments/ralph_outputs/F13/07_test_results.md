# 07 — Test Results

## Command
```
$ python3 experiments/ralph_outputs/F13/artifacts/validate_poster.py
```

## Output (real)
```
=== F13 poster validation ===
repo root: /Users/mei/rl
required sections present (md): ['Motivation', 'Method', 'Benchmark', 'Results', 'Takeaways']
cited repo file-paths checked: ['agent/llm.py', 'docs/ENVIRONMENT_DESIGN.md',
  'docs/headline_insights.md', 'rex/frontier.py', 'rex/harness_synth.py', 'rex/loop.py',
  'rex/runs/ablation.json', 'rex/scoring.py', 'sim/engine.py']

PASS: poster.md + poster.html valid, well-formed, print-styled, sources exist.
EXIT=0
```

## Structure check (real)
```
$ python3 -c "..."   # count panels
html bytes: 11962
sections: 10
tables: 1
md bytes: 6445
```

## Test-case results
| ID | Check | Result |
|----|-------|--------|
| T1 | poster.md has all 5 required sections | PASS (0 missing) |
| T2 | poster.html well-formed (tag stack balances, void elems handled) | PASS (0 errors) |
| T3 | poster.html has `@page`, `@media print`, `size: A0` | PASS |
| T4 | no placeholder tokens (lorem/TODO/FIXME/xxxx) in either file | PASS |
| T5 | every cited `[src:]` repo file-path exists on disk | PASS (9/9 exist) |

## Fixes applied during testing
- None required — validator passed on first run. The void-element handling added during the
  ouroboros step (Engineer A) prevented the expected false positives on `<meta>`/`<br>`.

## Notes / honest limits
- The validator checks well-formedness and presence, not pixel-level print fidelity. Visual
  A0 layout fit was reasoned about (conservative font sizes, `overflow` guards, `margin:0`)
  but not rasterized here — final raster is a downstream design step (stated in the poster
  footer). No headless-browser render was run (no such tooling assumed in this env).
