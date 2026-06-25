# B9 — 07 Test Results

## 1. Unit tests — PASS (12/12)
```
$ python3 experiments/ralph_outputs/B9/artifacts/test_bootstrap_ci.py
PASS percentile median
PASS percentile lo clamp
PASS percentile hi clamp
PASS all-pass point=1
PASS all-pass CI degenerate
PASS all-fail CI degenerate
PASS 50/50 point=0.5
PASS 50/50 CI brackets point
PASS 50/50 SE ~ sqrt(pq/n)
PASS deterministic given seed
PASS cluster width >= plain width on clustered data
PASS wilson matches formula

ALL TESTS PASSED
```

## 2. Main run — PASS
```
$ python3 .../bootstrap_ci.py --resamples 10000 --seed 12345 --out .../bootstrap_ci_results.json
condition           pass@1          Wilson 95%         Bootstrap 95%        Cluster-boot 95%
------------------------------------------------------------------------------------------------
zero_shot            0.000  [0.000,0.204]      [0.000,0.000]        [0.000,0.000]
best_of_n            0.067  [0.012,0.298]      [0.000,0.200]        [0.000,0.200]
retry_realistic      0.000  [0.000,0.204]      [0.000,0.000]        [0.000,0.000]
rex                  0.400  [0.198,0.643]      [0.133,0.667]        [0.000,0.800]
rex_no_oracle        0.000  [0.000,0.204]      [0.000,0.000]        [0.000,0.000]
wrote experiments/ralph_outputs/B9/artifacts/bootstrap_ci_results.json
```

## 3. Cross-check vs shipped pipeline — PASS
`experiments/compute_pass_at_k.py` (DIAGRAM 4) reports the SAME pass@1 and the SAME
Wilson CIs: rex 0.400 [0.198,0.643], best_of_n 0.067 [0.012,0.298], the rest 0.000
[0.000,0.204]. Bootstrap point estimates therefore match the canonical numbers exactly.
The per-incident breakdown from that tool also confirms the clustering driving the wide
cluster CI: rex = aws_dynamodb_dns 3/3, railway_gcp_suspension 3/3, cloudflare_waf 0/3,
crowdstrike_bsod 0/3, azure_ddos 0/3.

## 4. Determinism — PASS
Re-ran with `--seed 12345`; the `conditions` block is byte-for-byte identical
(`identical: True`).

## 5. Syntax — PASS
`ast.parse` clean on both `bootstrap_ci.py` and `test_bootstrap_ci.py`.

## Fixes applied during testing
- **`REPO` path bug:** initially `parents[3]` pointed at `experiments/rex/runs/...` →
  `FileNotFoundError`. Fixed to `parents[4]` (artifacts→B9→ralph_outputs→experiments→rl).
  The loud failure caught it immediately; `--data` override added as a safety valve.
