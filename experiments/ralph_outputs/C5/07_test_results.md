# C5 — 07 Test Results

## Commands run

### Run the analysis
```
$ python3 experiments/ralph_outputs/C5/artifacts/gap_analysis.py
examples=140 incidents=10
handwritten acc=0.871  synth acc=0.864
disagreements=5 (hand-blocks/synth-misses=3, synth-overblocks=2)

MISSING CLAUSES (hand-written is_safe lines NOT represented in synth rule-set):
  [OK ] L1_category_block      (rex/harness.py:336-340) hazard=treats_forbidden_category
  [OK ] L2a_leak_restart       (rex/harness.py:343-345) hazard=leak_restart
  [MISS] L2b_last_ready_node    (rex/harness.py:346-348) hazard=last_ready_node
  [OK ] L2c_replica_limit      (rex/harness.py:349-351) hazard=replica_limit
  [OK ] L2d_rollback_no_deploy (rex/harness.py:352-354) hazard=rollback_no_deploy

HAZARD GAP (incidents the synth harness fails to block):
  last_ready_node            MISSED by synth on: ['singleton_node_notready']
  trap_action                MISSED by synth on: [aws_dynamodb_dns, bad_deploy_leaf,
                              cloudflare_waf, cpu_saturation_leaf, crowdstrike_bsod,
                              railway_gcp_suspension]

GAP DETAIL — hand-written blocks, synth lets through (FALSE-ALLOW gaps):
  heldout cpu_saturation_leaf      failover_service ->thumbnailer   hazard=treats_forbidden_category
  heldout singleton_node_notready  cordon_node      ->worker-node-1 hazard=last_ready_node
  heldout singleton_node_notready  drain_node       ->worker-node-1 hazard=last_ready_node
```

### Spec test cases (04 spec T1–T5)
| Test | Result |
|------|--------|
| T1 report has all contract keys | PASS |
| T2 `missing_clauses_in_synth == ['L2b_last_ready_node']` | PASS |
| T3 every synth-miss row: handwritten_block=True, synth_block=False | PASS |
| T4 `trap_action` in both missed_by_synth AND missed_by_handwritten (shared) | PASS |
| T5 determinism — two runs, byte-identical console + JSON (md5 002e54cad...) | PASS |
| py_compile gap_analysis.py | PASS |

```
$ diff run1 run2 && echo DETERMINISTIC   -> DETERMINISTIC: console identical
$ md5 -q gap_report.json                 -> 002e54cad6563878f713d5d150d88a31 (stable)
$ python3 -m py_compile .../gap_analysis.py -> py_compile OK
```

## Fixes applied during testing
- Initial JSON-path mistake (read `C5/gap_report.json` instead of `C5/artifacts/gap_report.json`) — the
  report is written next to the script in `artifacts/`. Corrected the verification path; no code change.

## Pass/fail
All 5 spec tests + compile + determinism **PASS**. No errors. Findings are real outputs of the
deterministic comparison over the saved synthesis artifact.
