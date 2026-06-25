# 06 — Implementation

## Artifacts created (all task-namespaced; NO core files edited)
- `artifacts/lambda_sweep.py` — the sweep driver (offline default + `--real`).
- `artifacts/lambda_sweep_offline.json` — full offline sweep result (6 lambdas, budget 8).
- `artifacts/lambda_sweep_real.json` — real-API subset attempt → documented billing blocker.
- `artifacts/test_lambda_sweep.py` — 6 pytest tests over the driver's pure pieces.

## Design (how the sweep avoids touching the core)
`COMPLEXITY_LAMBDA` is a module constant read only inside `harness_synth.train_score`.
Rather than monkey-patch it, the driver defines `score_with_lambda(rs, ex, lam)` — a faithful
copy of `train_score`'s math with lambda as a parameter — and passes it as the `evaluate=`
callback to `rex.tree.thompson_search`. `propose=` is either:
- **offline** (default): `propose_offline_builder` — a deterministic greedy hill-climb that
  adds the single best general block-rule atom (one bool feature, one tool) per step, where
  "best" is measured by `score_with_lambda` itself. So lambda directly governs how many
  conditions survive. No network.
- **real**: delegates to `harness_synth.propose_ruleset` (haiku mutation operator).

`confusion`, `confusion_pred`, `handwritten_pred`, `validate_ruleset`, `labeled_examples`,
`TRAIN`, `HELDOUT` are imported unchanged — the rule semantics are exactly the core's.

## What I did NOT do
- Did NOT edit `rex/harness_synth.py`, `rex/tree.py`, `rex/harness.py`, or any shared file.
- Did NOT change `COMPLEXITY_LAMBDA`. The sweep is purely additive via the driver.

## Result (offline, deterministic, budget 8)
Hand-written `is_safe` baseline (lambda-independent): TRAIN acc 0.842, HELD-OUT acc 0.949.
Reference real haiku synthesis at default lambda (from committed `rex/runs/harness_synth.json`):
TRAIN acc 0.861, HELD-OUT acc 0.872 — the offline operator below is a *weaker stand-in*.

| lambda | rules | conds | TRAIN acc | TRAIN FA | HELD-OUT acc | HELD-OUT FA |
|-------:|------:|------:|----------:|---------:|-------------:|------------:|
| 0.0    | 3 | 3 | 0.713 | 29 | 0.744 | 10 |
| 0.003  | 3 | 3 | 0.713 | 29 | 0.744 | 10 |
| 0.01   | 3 | 3 | 0.713 | 29 | 0.744 | 10 |
| 0.03   | 2 | 2 | 0.693 | 31 | 0.718 | 11 |
| 0.08   | 0 | 0 | 0.634 | 37 | 0.667 | 13 |
| 0.2    | 0 | 0 | 0.634 | 37 | 0.667 | 13 |

(The 3 rules at low lambda all block a node/network tool when
`treats_forbidden_category==True` — the spanning hazard.)

## Reading of the curve
- **Low lambda (0–0.01):** the penalty is a pure tie-breaker; it changes nothing about which
  rules are kept (3 rules, identical accuracy). This is exactly the design intent of the
  default `0.003` — "never enough to outweigh a single misclassification".
- **Mid lambda (0.03):** the penalty starts pricing out a marginal rule (3→2 rules); held-out
  accuracy drops and a held-out false-allow appears. Under-fitting begins.
- **High lambda (≥0.08):** the penalty exceeds every atom's reward gain → the search stalls at
  the EMPTY rule-set. The harness is silently disabled: it allows every action, so all 13
  held-out should-block actions become false-allows. This is the safety-critical headline:
  an over-large complexity penalty can collapse the synthesized harness to "allow everything".
