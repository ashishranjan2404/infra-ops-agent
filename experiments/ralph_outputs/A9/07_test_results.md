# A9 — 07 Test Results

All commands run from `experiments/ralph_outputs/A9/artifacts/` with Python 3.13.

## T1 — build validator passes, count matches YAMLs — PASS
```
$ python3 build_mttr_json.py --check
VALIDATION OK
{ "total_incidents": 51, "real_incidents": 30, "synthetic_incidents": 21,
  "mttr_labeled": 18, "real_but_unknown_mttr": 12, "coverage_of_real_pct": 60.0 }
```
`total_incidents=51` equals the number of YAMLs in `scenarios/cidg/generated/`.

## T2 — validator rejects a bad confidence value — PASS
Injected `confidence=BOGUS` into one row:
```
$ python3 build_mttr_json.py --check
VALIDATION FAILED:
  - redis-cache-flush: bad confidence 'BOGUS'
exit=1
```
(CSV restored afterward; JSON rebuilt clean.)

## T3 — every incident_id matches a YAML meta.id, no missing/extra — PASS
```
mismatches: none
yaml-not-in-csv: none
rows=51 yamls=51
```

## T4 — correlation stub runs end-to-end on repo assets — PASS
```
$ python3 correlate_mttr.py
paired=18  dropped=33
  dropped <33 unknown-MTTR/synthetic incidents, each with reason>
signal = structural_proxy
pearson(mttr, structural_proxy)  = <printed>
spearman(mttr, structural_proxy) = <printed>
per-incident: <18 rows, mttr descending>
```
18 paired == 18 known-MTTR incidents; 33 dropped == 12 unknown-real + 21 synthetic.

## T5 — unknown MTTR serializes as JSON null — PASS
```
$ python3 -c "...launchdarkly-cold-cache..."
mttr_minutes is None      # -> serialized as null in mttr_labels.json
```

## Notes / fixes applied during testing
- Fixed a CSV/notes inconsistency on `github-network-partition` (1466 -> 1451 to
  match the documented 24h11m).
- Detected mid-run YAML additions by other workers (A5: 80-89 set; A11: a11-pair-*)
  via T3 and labelled all of them; coverage went 32 -> 45 -> 51 incidents, all
  re-validated.
