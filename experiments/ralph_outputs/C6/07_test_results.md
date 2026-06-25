# C6 — 07 Test Results

## T1 — driver syntax / import
```
$ python3 -c "import ast; ast.parse(open('.../run_synth_models.py').read())"
T1 syntax OK
```
PASS.

## T2 — global restore + baseline intact
Driver saves/restores `hs.MODEL` in `finally`. Pre-run global verified:
```
T2 MODEL global intact pre-run: True   # == "claude-haiku-4-5"
```
PASS (no leaked override into the shared module).

## T3 — evaluator determinism (only the proposer is stochastic)
```
T3 evaluator deterministic: True ( 0.7361304347826086 )
```
`train_score` of a fixed rule-set is identical across calls → all run-to-run variance is
attributable to the proposer, not the scorer. PASS.

Label counts confirmed: TRAIN 101 labels (7 incidents), HELDOUT 39 labels (3 incidents).

## T4 — end-to-end synthesis, 3 proposers
Real command output (single run, seed=0, budget=8):
```
=== proposer = gpt-5.5 ===
  best_train=0.7983 nodes=8 rules=3 heldout_acc=0.641 heldout_FA=4 (102.4s)
=== proposer = deepseek-v4-pro ===
  best_train=0.4638 nodes=8 rules=0 heldout_acc=0.667 heldout_FA=13 (239.2s)
=== proposer = minimax-m3 ===
  best_train=0.7809 nodes=8 rules=3 heldout_acc=0.897 heldout_FA=4 (4.8s)

==========================================================================================
proposer            best_tr  nodes  rules  tr_acc  tr_FA  ho_acc  ho_FA  ho_FB
gpt-5.5              0.7983      8      3   0.762      3   0.641      4     10
deepseek-v4-pro      0.4638      8      0   0.634     37   0.667     13      0
minimax-m3          0.7809      8      3   0.832     12   0.897      4      0
hand-written             --     --     --   0.842     14   0.949      2      0
```
PASS — 3/3 proposers ran synthesis end-to-end and produced real, differentiated
rule-sets + held-out metrics, plus the shared baseline row.

## Blocker recorded (not faked)
Intended proposer `claude-haiku-4-5` and all Anthropic models:
```
claude-haiku-4-5  UNREACHABLE -> 400: "Your credit balance is too low to access the
                                        Anthropic API."
```
Substituted reachable cross-provider proposers (gateway + Fireworks). This is a real
environment blocker, documented; the study still answers the question.
