# 07 — Test Results

## Extractor run (real repo)
```
$ python3 extract_trap_taxonomy.py
scenarios=51 with_trap=51 trap_penalty=0.6 tools={'scale_deployment': 48, 'restart_pod': 1, 'rollback_deployment': 1, 'restart_service': 1}
```

## Pytest
```
$ python3 -m pytest test_extract_trap_taxonomy.py -q
......                                                                   [100%]
6 passed in 0.71s
```

| Test | Checks | Result |
|---|---|---|
| test_constants_match_scoring | TRAP_PENALTY==0.60, weights sum to 1.0 | pass |
| test_every_record_has_a_trap_tool | coverage ≥ 90%, every trap names a tool | pass (51/51) |
| test_scale_deployment_is_modal_trap | scale_deployment is the modal trap | pass (48) |
| test_every_trap_contrasted_with_a_real_fix | every trap has a non-empty gold fix | pass |
| test_why_table_extracted_if_present | why-table includes scale_deployment | pass |
| test_main_writes_valid_json | main() writes parseable JSON | pass |

## Validation of generated artifact
```
$ python3 -c "import json;d=json.load(open('trap_taxonomy.json')); \
  print(d['why_table_tools']); print(sum(1 for r in d['records'] if r['why_label']))"
['clear_cache', 'restart_service', 'scale_deployment']
49
```
- 49/51 records carry a `why_label` (the 2 without are `restart_pod` /
  `rollback_deployment`, which are not in scoring.py's `why` table — correctly returned as
  null rather than fabricated).

## Markdown parse-check
`comparison_report.md` parses (table renders; 8 sections present). No broken artifacts.

## Fixes applied during dev
- The `why` dict in scoring.py is the receiver of a `.get()` call, not a bare assignment, so
  the initial AST plan (literal_eval of a line) was replaced by a Dict-node walk keyed on
  known trap tools (as flagged in 05_ouroboros, Engineer 1). Verified it extracts 3 tools.
