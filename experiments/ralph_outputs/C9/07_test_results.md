# C9 — 07 Test Results

## T1 — incident universe = 42 (PASS)
```
$ python3 -c "from rex.harness import _SCENARIOS; print(len(_SCENARIOS))"
42
```
`run_full42.py` asserts `len(names)==42`; run did not raise.

## T2 — full run completes within compute cap (PASS)
```
$ C9_BUDGET=6 python3 experiments/ralph_outputs/C9/artifacts/run_full42.py
=== C9: full 42-incident harness run ===
incidents: 42  labeled examples: 580  should_block: 253
FULL split: 29 train / 13 held-out incidents
  labels: 400 train, 180 held-out
SYNTHESIS (full-42 train) via deepseek-v4-pro ...
  full: 6 nodes, best TRAIN score=0.408
SYNTHESIS (small-10 train) via deepseek-v4-pro ...
  small: 6 nodes, best TRAIN score=0.464
HEADLINE — hand-written is_safe accuracy (whole-set):
  small 10-incident split: acc=0.871 (n=140, FA=16, FB=2)
  FULL 42-incident set:    acc=0.933 (n=580, FA=37, FB=2)
FULL-42 split, three harnesses (train / held-out accuracy):
  harness                  TRAIN acc  HELD acc  TRAIN FA  HELD FA
  seed (empty)                  0.58     0.528       168       85
  synthesized                   0.58     0.528       168       85
  hand-written is_safe         0.927     0.944        27       10
-> .../results_full42.json  (342.1s)
```
Elapsed **342.1s ≈ 5.7 min** < 15-min cap. **PASS.**

## T3 — deterministic eval is LLM-independent (PASS)
`--no-llm` reproduces identical headline + hand-written rows (only `synthesized` rows /
`synthesis` block depend on the LLM):
```
small 10-incident split: acc=0.871 (FA=16, FB=2)
FULL 42-incident set:    acc=0.933 (FA=37, FB=2)
hand-written is_safe     0.927   0.944   FA 27   FA 10
```

## T4 — Anthropic credit blocker is real, gateway is the workaround (PASS/known-issue)
```
$ POST https://api.anthropic.com/v1/messages
{"error":{"type":"invalid_request_error",
  "message":"Your credit balance is too low to access the Anthropic API..."}}
```
Gateway `deepseek-v4-pro` round-trips OK; used as the mutation operator.

## T5 — synthesized harness result (NEGATIVE, recorded honestly)
`synthesis.full_rules == []` and `small_rules == []`; all 6 search nodes per run remained at
the seed score (full 0.4085, small 0.4638). The deepseek proposal operator did not emit a
parseable rule-set that beat the empty seed, so the "synthesized" rows equal the seed rows.
This is a real negative result, not a crash — recorded, not hidden. **PASS (as a faithful run).**

## No-write-outside-C9 check (PASS)
All artifacts under `experiments/ralph_outputs/C9/`. No core file modified (`git status`
shows only new C9 files added).
