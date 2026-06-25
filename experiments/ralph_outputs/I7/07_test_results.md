# 07 — Test Results

## Classifier run
```
$ python3 experiments/ralph_outputs/I7/artifacts/classify_traps.py
input: G4/trap_taxonomy.json
scenarios with a trap: 51
counts per category:
  scale-trap      48  ################################################
  restart-trap     2  ##
  rollback-trap    1  #
  failover-trap    0
  other-trap       0
dominant: scale-trap (94.1% of all traps)
EMPTY (no coverage): failover-trap, other-trap
wrote .../trap_classification.json
=== EXIT 0 ===
```

## Unit tests
```
$ python3 -m pytest experiments/ralph_outputs/I7/artifacts/test_classify_traps.py -q
....                                                                     [100%]
4 passed in 0.03s

$ python3 experiments/ralph_outputs/I7/artifacts/test_classify_traps.py
PASS test_build_on_real_repo
PASS test_skew_is_reported
PASS test_tool_mapping
PASS test_unknown_tool_is_other
```

## Validation checks
- `pyyaml` import OK.
- All 7 markdown files non-empty and parse.
- `trap_classification.json` is valid JSON; `distribution` has all 5 keys; sums to
  51 (== `n_scenarios_with_trap`).

## Fixes applied during dev
None required — first run passed. The two-restart count (`restart_pod` +
`restart_service`) correctly folds into `restart-trap`, which I verified against the
G4 tool distribution (`restart_pod:1, restart_service:1, rollback_deployment:1,
scale_deployment:48`).

## Result: PASS
Classifier runs, exits 0, all tests green, output internally consistent.
