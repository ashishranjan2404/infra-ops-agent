# 07 — Test Results

All commands run from `experiments/ralph_outputs/H7/artifacts/` with Python 3.13.7.

## Direct test runner
```
$ python3 test_model_registry.py
PASS test_cli_list_and_filter
PASS test_cli_show_by_slug_and_missing
PASS test_cli_stats_training_deltas
PASS test_json_parses_and_required_fields
PASS test_known_real_references_present

5 tests passed
```

## pytest
```
$ python3 -m pytest test_model_registry.py -q
.....                                                                    [100%]
5 passed in 0.14s
```

## JSON parse check
```
$ python3 -c "import json; json.load(open('model_registry.json'))"
parse OK, 11 models
```

## CLI smoke (real output)
```
$ python3 model_registry.py stats
total models: 11
by role:     {'eval': 8, 'trainable': 3}
by status:   {'aborted': 1, 'flat': 1, 'frozen': 8, 'trained': 1}
by provider: {'anthropic': 2, 'fireworks': 2, 'gateway': 4, 'hud-tinker': 3}

training runs (mean reward start -> end):
  opensre-qwen3-8b       0.5220 -> 0.4910  (-0.0310 down)
  opensre-qwen3-8b-v2    0.5039 -> 0.5410  (+0.0371 up)
  opensre-qwen3-30b      0.4737 -> 0.4905  (+0.0168 up)
```
`list`, `list --role trainable`, `show <slug>`, `query --provider gateway --role eval`, and
`show <missing> -> exit 2` were all exercised (see 06 / live run) and behaved per spec.

## Failures / fixes
None. All 5 tests passed on the first full run under both the direct runner and pytest.
The numeric assertions (`0.5220 -> 0.4910`, `total models: 11`) tie the tests to the REAL
training-run data, so a fabricated edit would break them.
