# I6 — 07 Test Results

## pytest (7 cases)
```
$ python3 -m pytest test_failure_taxonomy.py -q
.......                                                                  [100%]
7 passed in 0.07s
```
Cases: precedence (trap>root_cause), no_fix-only, empty_plan→safe_abstain, clean_win
exclusion, **rescoring-replay detects a known trap via rex.scoring** (validates the HUD
path), probe recompute consistency, real-data end-to-end.

### Fix applied during testing
`@dataclass` failed to resolve its module when the script was loaded via `importlib`
(`AttributeError: 'NoneType' has no '__dict__'`). Fixed by registering
`sys.modules["ft"] = ft` before `exec_module`. No change to the tool itself; standard
importlib-loading idiom.

## Tool run on real data
```
$ python3 failure_taxonomy.py
Corpus: 57 rollouts (probe=12, hud=45).
Failure tail (score<1 OR any failed_check): 36 of 57. Clean wins: 21. Strict zero-reward: 0.
Primary buckets (of 36 failed): no_fix 22, wrong_root_cause 7, trap_taken 7, not_resolved 0.
[wrote] failure_report.json + failure_report.md
```

## Validation checks
- `python3 -m py_compile failure_taxonomy.py test_failure_taxonomy.py` → OK.
- `failure_report.json` parses as valid JSON; all 8 top-level keys present.
- The HUD replay is hermetic: `REX_JUDGE_MODE=deterministic` forced + `deterministic_judge`
  injected → no network call, reproducible.
- Probe rows with stored `failed_checks==["trap_action"]` bucket to `trap_taken`, and
  stored clean rows (score 1.0, no checks) bucket to `clean_win` — consistency asserted
  in `test_probe_recompute_matches_stored_failed_checks`.

## Known non-failures (honest)
- HUD `rex.score_plan` spans store no score response, so the HUD column is a *re-derivation*,
  not the original recorded reward. The replay-trap test is the evidence it matches the
  real scoring path; we cannot byte-compare against an original we don't have.
- Probe rows do not store the action plan, so HUD `attempted_trap` / `n_actions` info is
  unavailable for probe rows (n_actions defaults 0 there; this only adds `empty_plan` tags
  to probe rows, which is a benign over-tag noted in the critique).
