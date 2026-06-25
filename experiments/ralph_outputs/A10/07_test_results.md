# A10 — 07 Test Results

## Unit tests — `test_blast_radius.py`
Command:
```
python3 experiments/ralph_outputs/A10/artifacts/test_blast_radius.py
```
Output:
```
PASS test_fanout
PASS test_linear_chain_fault_at_dependency
PASS test_linear_chain_fault_at_top_caller
PASS test_no_edges
PASS test_real_scenario_consul
PASS test_tier_sev1_by_count
PASS test_tier_sev1_by_highsev_cascade
PASS test_tier_sev2_by_cascade
PASS test_tier_sev2_by_count
PASS test_tier_sev3_contained

10/10 passed
```
**Result: PASS (10/10).**

## End-to-end run over real scenarios
Command:
```
python3 experiments/ralph_outputs/A10/artifacts/blast_radius.py
```
Output:
```
Processed 33 incidents
  wrote experiments/ralph_outputs/A10/artifacts/blast_radius.json
  wrote experiments/ralph_outputs/A10/artifacts/blast_radius.csv
  tier distribution: {'SEV1': 24, 'SEV2': 1, 'SEV3': 8}
  multi-service blast: 25/33
```
**Result: PASS** — all 33 scenarios processed, no parse/runtime errors.

## Sidecar sanity checks
- JSON valid, `count == 33`, no duplicate incident ids.
- `mean services_affected == mean topology size == 3.52` → in every scenario the
  root cause reaches the whole declared topology (the root is always a sink
  dependency that all other nodes transitively call). Min 1 (synthetic single-node),
  max 5.
- 8 synthetic single-node scenarios → SEV3 (correct, contained).
- Real-incident scenarios (slack/github/cloudflare/aws/etc.) → SEV1/SEV2 with
  `cascades: true` (correct).

## Fixes applied during testing
None required — first run passed. Empirically validated edge direction before
coding (slack-consul-cache-db), so no inversion bug surfaced.
