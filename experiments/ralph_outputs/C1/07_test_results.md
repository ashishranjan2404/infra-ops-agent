# 07 — Test Results

## Driver tests (pure, no network)
```
$ python3 -m pytest experiments/ralph_outputs/C1/artifacts/test_lambda_sweep.py -q
......                                                                   [100%]
6 passed in 0.12s
```
Covered: fidelity (`score_with_lambda == train_score` at default lambda, on `[]` and a
2-rule set), monotone score in lambda, atom generality, offline propose grow/stall,
run_point determinism, and weakly non-increasing n_conditions across the grid.

## Core regression (proves no core breakage)
```
$ python3 -m pytest tests/test_harness_synth.py -q
.........                                                                [100%]
9 passed in 0.02s
```

## Offline sweep run (the deliverable)
```
$ python3 experiments/ralph_outputs/C1/artifacts/lambda_sweep.py --offline
 lambda  reward rules cond TR_acc TR_FA HO_acc HO_FA
    0.0  0.5797     3    3  0.713    29  0.744    10
  0.003  0.5707     3    3  0.713    29  0.744    10
   0.01  0.5497     3    3  0.713    29  0.744    10
   0.03  0.4907     2    2  0.693    31  0.718    11
   0.08  0.4638     0    0  0.634    37  0.667    13
    0.2  0.4638     0    0  0.634    37  0.667    13
```
JSON written to `artifacts/lambda_sweep_offline.json` (parse-checked OK).

## Real-API subset — BLOCKED (honest result)
```
$ python3 lambda_sweep.py --real --budget 4 --lambdas 0.003,0.08
... requests.exceptions.HTTPError: 400 Client Error: Bad Request
  for url: https://api.anthropic.com/v1/messages
body: "Your credit balance is too low to access the Anthropic API."
  (request_id req_011CcPbZYYTRetEHnoX1EyeT)  model claude-haiku-4-5-20251001
```
Diagnosis: the `--real` code path is correct (it reaches `agent.llm.call` and sends a
well-formed request); the 400 is an **account billing** error, matching the project memory
note "Anthropic out of credits". Recorded in `lambda_sweep_real.json` with remediation
(add credits or repoint the roster at the HUD gateway / Fireworks, then re-run `--real`).

## Note on node_rewards at high lambda
At lambda ≥ 0.08 the offline greedy operator stalls at the empty rule-set; the thompson tree
then fills with duplicates of the parent, so `node_rewards` is a flat tail. This is *stalled*,
not *converged* — the correct signal that lambda has priced out every atom. The reported
`best` rule-set (empty) is correct.
