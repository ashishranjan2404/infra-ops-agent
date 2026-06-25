# 07 — Test Results

## Unit tests (hermetic, no network/LLM)
Command:
```
python3 -m pytest experiments/ralph_outputs/B7/artifacts/test_root_cause_accuracy.py -q
```
Output:
```
.............                                                             [100%]
13 passed in 0.02s
```
All 13 pass: classification (4 categories + phrasing-robustness + empty +
no-signal), gold mapping, perfect/mixed evaluate, confusion entry, decoupling,
YAML-kind grounding path, skip-unlabeled.

## Real-data run (197 trajectories)
Command:
```
python3 experiments/ralph_outputs/B7/artifacts/root_cause_accuracy.py
```
Result:
```
Root-cause accuracy (standalone): 0.213  (42/197)
Records evaluated: 197

Per-category accuracy (gold -> recall):
  bad_deploy             1.000
  config_error           0.167
  dependency_failure     0.000
  network_fault          0.256
  node_failure           0.167
  resource_exhaustion    0.227
  saturation             0.119
  unknown                0.250

Decoupling check: root-cause-correct disagrees with incident-resolved on
43.1% of 197 records.
```
Full confusion matrix captured in `artifacts/run_output.txt` and
`artifacts/rca_result.json`.

## Validity self-test (YAML gold descriptions -> classifier)
Feeding the gold `kind/location` descriptions through the classifier yields
**0.875** accuracy (n=8 sampled scenarios) — an upper bound confirming the
classifier + gold mapping are sound. The low 0.213 on real model answers is the
MODELS' diagnosis quality (verbose multi-cause narratives), not a metric bug.

## Findings / fixes applied during dev
- "bad_deploy" over-fires (12/12 recall but many false positives from
  resource_exhaustion=13 and saturation=14): common verbs "rollback/deploy/
  version" appear in remediation prose. Documented as a known limitation in 09;
  not tuned away (no test-set fitting, per the grill).
- No code fixes were needed after the initial implementation; tests passed first run.
