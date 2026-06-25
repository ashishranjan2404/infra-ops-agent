# C1 - Lambda Sweep over Harness-Synthesis Complexity Penalty - SUMMARY

## Task
Run harness synthesis (rex/harness_synth.py) with different complexity penalties
(COMPLEXITY_LAMBDA, default 0.003) and report how the synthesized rule-set and accuracy
change with lambda. No core-file edits - new driver only. Compute cap ~15 min.

## What was built (all under C1/artifacts/, no core edits)
- lambda_sweep.py - sweep driver. Avoids editing the core by re-implementing the reward as
  score_with_lambda(rs, ex, lam) and injecting it as evaluate= to rex.tree.thompson_search.
  Offline deterministic operator (default, no network) + --real haiku operator.
- lambda_sweep_offline.json - full offline sweep (6 lambdas, budget 8).
- lambda_sweep_real.json - real-API attempt, blocked by Anthropic billing (documented).
- test_lambda_sweep.py - 6 tests; includes a sub-1e-12 fidelity assertion that
  score_with_lambda(rs, ex, 0.003) == harness_synth.train_score(rs, ex).

## Result (offline, deterministic; baselines computed live)
Hand-written is_safe baseline (lambda-independent): TRAIN acc 0.842, HELD-OUT acc 0.949.
Reference real haiku synthesis @ default lambda (committed run): TRAIN 0.861, HELD-OUT 0.872.

| lambda | rules | conds | TRAIN acc | HELD-OUT acc | HELD-OUT false-allow |
|-------:|------:|------:|----------:|-------------:|---------------------:|
| 0.0    | 3 | 3 | 0.713 | 0.744 | 10 |
| 0.003  | 3 | 3 | 0.713 | 0.744 | 10 |
| 0.01   | 3 | 3 | 0.713 | 0.744 | 10 |
| 0.03   | 2 | 2 | 0.693 | 0.718 | 11 |
| 0.08   | 0 | 0 | 0.634 | 0.667 | 13 |
| 0.2    | 0 | 0 | 0.634 | 0.667 | 13 |

Finding: lambda in [0, 0.01] is a pure tie-breaker (no change - exactly the default intent).
At lambda 0.03 it begins pricing out a rule -> under-fitting (held-out accuracy drops, a
held-out false-allow appears). At lambda >= 0.08 the search collapses to the EMPTY rule-set:
the synthesized harness is silently disabled and every should-block action becomes a
false-allow. That collapse is the safety-relevant headline.

## Status: completed (real-haiku sweep scaffolded but blocked by Anthropic billing)
The offline operator is a deterministic, weaker stand-in for the haiku operator; the
deliverable characterizes the shape of the lambda response + the collapse threshold, not the
production system absolute accuracy. Tests: 6/6 driver + 9/9 core green. No core files modified.
