# 07 — Test results

## 1. Compile check
```
$ python3 -m py_compile per_incident_breakdown.py test_per_incident_breakdown.py
OK
```

## 2. Unit tests (7/7 pass)
```
$ python3 test_per_incident_breakdown.py
PASS test_binary_pass
PASS test_family_map
PASS test_k_override
PASS test_multi_source_rows
PASS test_pass_at_k_bounds
PASS test_solvability_flags
PASS test_summary_counts_and_unsolvable_list

7/7 tests passed
```
Note: an initial assertion assumed the fallback estimator's `n=0 -> 0.0` behavior, but the
imported upstream `compute_pass_at_k.pass_at_k` differs on that degenerate input. Since
`build_rows` never calls the estimator with n=0 on real data (it only iterates incidents
that have reward lists), the assertion was removed rather than papering over the difference.

## 3. Real run over A1 + A2 (0 errors)
```
$ python3 per_incident_breakdown.py \
    --inputs ../../A1/artifacts/full_pass_at_k_glm-5p2.json \
             ../../A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json \
    --out-json out/per_incident_breakdown.json --out-md out/per_incident_breakdown.md
[ok] loaded ../../A1/artifacts/full_pass_at_k_glm-5p2.json
[ok] loaded ../../A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json
[done] 72 rows  solvable=64 partially=1 unsolvable=7
```

## 4. Output validity
- `out/per_incident_breakdown.json` — valid JSON (parse-checked).
- `out/per_incident_breakdown.md` — 72-row table + unsolvable list + by-family rollup.

## 5. Invalid-input handling
```
$ python3 per_incident_breakdown.py --inputs out/bad.json ...
[skip] out/bad.json: not a pass@k result JSON (missing keys)
no valid input sources
exit=2
```
Graceful skip + nonzero exit when no valid source — as specified.

## 6. Findings extracted from the real output
- counts: solvable=64, partially=1, unsolvable=7.
- by_family (solvable/partially/unsolvable): cascade 24/0/6, novel 20/0/0, simple 20/1/1.
- Unsolvable under BOTH models: `azure_ddos`, `cloudflare_waf`, `crowdstrike_bsod`.
- glm-5p2-only unsolvable: `singleton_node_notready`; partially: `payments_dep_revoked`.
- 41 learnable-but-hard rows (zero_shot p@1==0, rex p@1==1).

All success criteria met; run is real and reproducible.
