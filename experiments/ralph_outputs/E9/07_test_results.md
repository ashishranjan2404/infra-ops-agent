# E9 — 07 Test Results

## Commands run (real output)

### Self-test (hermetic, no files/network)
```
$ python3 artifacts/synth_sre_augmenter.py --self-test
  [PASS] 3 variants produced
  [PASS] has positive
  [PASS] has trap negative
  [PASS] has empty negative
  [PASS] positive reward == 1.0
  [PASS] trap reward < 0 (penalty)
  [PASS] empty plan reward == 0
  [PASS] within-group spread > 0
  [PASS] deterministic re-run
ALL PASS
```

### Run over all 51 CIDG scenarios
```
$ python3 artifacts/synth_sre_augmenter.py --scenarios scenarios/cidg/generated --n 4 \
    --out artifacts/augmented_trajectories.jsonl
{"scenarios": 51, "groups": 204, "trajectories": 816, "groups_with_spread": 204,
 "mean_within_group_spread": 0.5745, "out": ".../augmented_trajectories.jsonl"}
```

### JSONL integrity + spread check
```
parsed 204 groups OK; groups with zero spread: 0
```
Every group is well-formed, every group has positive within-group reward spread.

### Determinism
```
BYTE-IDENTICAL across runs
```
Re-running the augmenter produced a byte-identical JSONL (SHA1-seeded RNG, no wall-clock).

### Comparison harness
```
comparison_result.json written
comparison_result.json valid JSON
```

## Comparison verdict (from comparison_result.json)
| metric | fireball_transfer | synthetic_sre_aug |
|---|---|---|
| status | **blocked** | runnable |
| n_trajectories | 0 | **816** |
| label_coverage (canonical vocab) | 0.0 | 0.10 |
| mean_within_group_spread | null | **0.5745** |
| domain_match | 0.0 | **1.0** |
| floor_check_pass | null | **true** |

Verdict: **synthetic_sre_augmentation** wins *on available evidence* — with the explicit
caveat that the Fireball arm was never run end-to-end (data-quality verdict, not accuracy).

## Honest finding (under-counted coverage)
`label_coverage` reads only **0.10**, but this is a **vocabulary-naming artifact**, not a real
diversity deficit. The augmented set actually covers **15 distinct raw `root_cause.kind`
mechanisms**:
`bad_content, bad_revision, cache_flush, cert_expire, churn_spike, config_bloat, cpu_starve,
dep_revoked, disk_fill, fd_exhaust, mem_leak, net_delay, node_notready, pool_leak,
thread_exhaust`.
Only `cache_flush` and `fd_exhaust` string-match the canonical `SRE_CLASSES` set in
`compare_arms.py`; the rest are differently *named* (e.g. `cpu_starve` vs `cpu_saturation`,
`mem_leak` vs `memory_leak`). The metric is reported as-is and this discrepancy is flagged
rather than hidden — a vocabulary-alignment map would lift coverage to ~0.7+.

## Fixes applied during testing
- Pinned reward constants + asserted `positive==1.0` in self-test (catches rubric drift).
- Surfaced `classes_covered` in the result so the coverage number is auditable.
