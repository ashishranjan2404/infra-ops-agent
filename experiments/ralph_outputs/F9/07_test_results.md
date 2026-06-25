# 07 — Test Results

## Generator run (real corpus)
```
$ python3 experiments/ralph_outputs/F9/artifacts/gen_incident_catalog.py
Parsed 51 incident specs from /Users/mei/rl/scenarios/cidg/generated
Wrote markdown catalog: .../incident_catalog.md
Wrote JSON index:       .../incident_catalog.json
```
PASS — all 51 YAML files parsed; **0 skipped** (no stderr WARN emitted).

## Unit / integration tests
```
$ python3 experiments/ralph_outputs/F9/artifacts/test_catalog.py
ok test_extract_minimal
ok test_extract_missing_keys
ok test_real_yamls_all_parse (51 specs)
ok test_generated_outputs_consistent (51 ids present)
ALL PASS    (EXIT=0)
```
- `test_extract_minimal` — full spec extraction, ordered fix string. PASS
- `test_extract_missing_keys` — empty `{}` spec does not crash; fix == "(none)". PASS
- `test_real_yamls_all_parse` — 51 real specs parsed, each has id + "@" in root cause. PASS
- `test_generated_outputs_consistent` — every JSON id present in MD; header count matches. PASS

## Static checks
```
$ python3 -m py_compile gen_incident_catalog.py test_catalog.py
compile ok
$ python3 -c "import json; json.load(open('incident_catalog.json'))"   # 51 rows
```
PASS — both scripts byte-compile; JSON parses (51 rows).

## Output sanity
- `incident_catalog.md`: 650 lines, 39 KB — Summary + 51-row table + 51 detail blocks.
- `incident_catalog.json`: 51 rows, 33 KB.
- Failure-class histogram (from Summary): config_bloat 7, bad_revision 6, cert_expire 6,
  fd_exhaust 6, net_delay 5, churn_spike 4, mem_leak 4, dep_revoked 3, cache_flush 2,
  cpu_starve 2, thread_exhaust 2, bad_content 1, disk_fill 1, node_notready 1, pool_leak 1.
- Aggregate: 40/51 cascade, 40/51 hidden root cause, 15 failure classes.

## Fixes applied during testing
None required — generator and tests passed on first full run after authoring
(defensive extraction designed up front from the ouroboros critiques).
