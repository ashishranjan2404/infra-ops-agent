# A7 — 07 Test Results

All tests run from repo root with `python3` (3.13) + pyyaml. Real output below.

## Script run (real)
```
scored 48 incidents
  expected_pass_rate: min=0.433 mean=0.560 max=0.873
  trap_complexity:    min=0.062 mean=0.593 max=0.791
  buckets: easy=11 medium=23 hard=14
wrote .../difficulty_scores.json
wrote .../difficulty_scores.csv
```

## Validation suite (T1–T7) — real output
```
T5 idempotent CSV: PASS (4fbe6a504014a941a29799b3fe21774f)
T7 source mtime unchanged: PASS
T1 all scores in [0,1]: PASS
T2 count==files: PASS   (33 at first run; 48 on rerun — both == disk)
T3 redis-cache-flush: easy tc=0.062 PASS
T4 cloudflare-waf-regex: medium tc=0.738 PASS
T6 breakdown keys present: PASS
```

| Test | Checks | Result |
|---|---|---|
| T1 | both metrics ∈ [0,1] for all incidents | PASS |
| T2 | json `count` == YAMLs on disk | PASS (48==48) |
| T3 | synthetic single-node ⇒ easy, tc<0.15 | PASS (tc=0.062) |
| T4 | cascading hidden postmortem ⇒ hard/medium, tc>0.6 | PASS (tc=0.738) |
| T5 | two runs ⇒ byte-identical CSV (md5) | PASS |
| T6 | JSON parses; breakdown keys present | PASS |
| T7 | source YAML mtime unchanged (non-mutation) | PASS |

## Fixes applied during testing
- Initial `head`-based inspection hid `80-gitlab-db-deletion.yaml`; confirmed
  the script's glob captured all files (count matched disk every run).
- Empty-`smoking_guns` guard and `None`-safe numeric coercion (from Ouroboros)
  verified: no scenario raised; all 48 scored without error.

## Concurrency observation (real, not a failure)
Between the first run (33 incidents) and the rerun (48) other parallel Ralph
workers added new scenario YAMLs. The scorer handled this transparently — it is
a pure read-only sidecar, so it neither corrupted nor was corrupted by the
concurrent writes. `json count == disk count` held on every run.

No test failures.
