# E7 — 07 Test Results

## Smoke run of the adapter
```
$ python3 experiments/ralph_outputs/E7/artifacts/trajectory_adapter.py
registered domains: ['alfworld', 'jericho', 'sre', 'textworld']
{ ...CanonicalTrajectory JSON for tw-demo... }
scoring inputs: {'stated_cause': 'opened the chest using the brass key',
                 'gold_root': 'open chest with brass key',
                 'red_herrings': ['eat key', 'go north into lava']}
```
PASS — module imports, registers all 4 domains, round-trips to JSON, and
projects into SRE scoring kwargs.

## Pytest
```
$ python3 -m pytest experiments/ralph_outputs/E7/artifacts/test_trajectory_adapter.py -q
............                                                             [100%]
12 passed in 0.02s
```
All 12 tests green. Full verbose capture in `artifacts/test_run.log`.

### Case-by-case
| test | result |
|---|---|
| all_domains_registered | PASS |
| adapt_produces_canonical[textworld/jericho/alfworld/sre] | PASS ×4 |
| step_indices_are_contiguous | PASS |
| actions_view | PASS |
| missing_gold_target_rejected (ValueError) | PASS |
| unknown_domain_raises (KeyError) | PASS |
| sre_scoring_inputs_shape | PASS |
| **adapted_game_traj_scorable_by_real_sre_judge** | PASS |
| distractors_flow_as_red_herrings | PASS |

## Validation of supporting artifacts
- `synthetic_fixtures.json` — valid JSON (loaded by the test's `json.load`).
- `TRANSFER_PLAN.md` — parses as markdown; no broken code fences.

## Fixes applied during dev
- Resolved `REPO_ROOT` relative to the test file (not cwd) so `import rex.scoring`
  is robust regardless of where pytest is launched (Engineer B / B1).

## Blocked (honest)
- Live transfer numbers (C0–C3 conditions): blocked — `textworld`/`jericho`/
  `alfworld` not installed, no network/ROMs in sandbox. Scaffold + protocol
  delivered instead.
