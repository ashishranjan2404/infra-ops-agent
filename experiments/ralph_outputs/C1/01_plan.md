# C1 — Lambda Sweep over Harness Synthesis Complexity Penalty

## Objective
`rex/harness_synth.py` synthesizes a SAFETY rule-set (DATA, not code) via Thompson-tree
search. The reward is `train_score()`, which subtracts a per-condition complexity
penalty `COMPLEXITY_LAMBDA * n_cond` (currently a hard-coded module constant `0.003`).
That penalty is a tie-breaker toward simpler / more-general rules.

**Task:** Run harness synthesis with *different* complexity penalties (a lambda sweep)
and report how the synthesized rule-set and its accuracy (TRAIN + HELD-OUT) change with
lambda. Specifically: does a larger lambda actually buy *generalization* (simpler rules
that transfer to held-out incidents), or does it under-fit (drop needed conditions →
false-allows)?

## Approach
- Write a NEW driver `artifacts/lambda_sweep.py`. Do NOT edit `rex/harness_synth.py`.
- Reuse the public surface of `harness_synth`: `labeled_examples`, `confusion`,
  `confusion_pred`, `handwritten_pred`, `propose_ruleset`, `TRAIN`, `HELDOUT`,
  and the generic `rex.tree.thompson_search`.
- The key trick: the module constant `COMPLEXITY_LAMBDA` is only *read* inside
  `train_score`. Instead of mutating the module, I define my OWN scoring closure
  `score_with_lambda(ruleset, train_ex, lam)` (a faithful copy of `train_score`'s
  math with lambda as a parameter) and pass it as `evaluate=` to `thompson_search`.
  This is a clean override with zero core edits.
- For each lambda in a sweep grid, run `thompson_search(propose=..., evaluate=...)`,
  take the best rule-set, and evaluate TRAIN/HELD-OUT confusion (accuracy, false-allow).
- Report: best TRAIN score, n_rules, n_conditions, TRAIN acc, HELD-OUT acc, false-allows,
  vs the hand-written `is_safe` baseline (lambda-independent).

## Compute cap (~15 min)
- A real run = budget(8) LLM mutation calls to `claude-haiku-4-5` PER lambda. A 6-point
  sweep = up to 48 haiku calls. That is feasible but flaky (needs ANTHROPIC_API_KEY).
- To GUARANTEE a runnable, reproducible result inside the cap, the driver has an
  `--offline` mode: a deterministic, local mutation operator (`propose_offline`) that
  builds candidate rule-sets from the *training mistakes* (greedy per-feature block
  rules) — no network. This is honest: it is a different (weaker) mutation operator, and
  I label results as such. I additionally attempt a SMALL real-API subset (2 lambdas,
  budget 4) if a key is present, and merge whatever I get.

## Files to create
- `artifacts/lambda_sweep.py` — the driver (offline + optional real-API modes).
- `artifacts/lambda_sweep_offline.json` — full offline sweep result.
- `artifacts/lambda_sweep_real.json` — real-API subset (if key present; else documented blocker).
- `artifacts/test_lambda_sweep.py` — pytest over the driver's pure pieces.

## Dependencies
- `rex.harness_synth`, `rex.tree`, `rex.harness` (all importable, no network for offline).
- Real-API mode needs `ANTHROPIC_API_KEY` in repo `.env`.

## Risks
- `train_score`'s exact formula must be replicated faithfully (2x weight on false-allow,
  maxerr normalization). Mitigation: at lambda=0.003 the offline/real score must match a
  direct `train_score` call → assert this in the test.
- Offline mutation may not reach the same rule-set the LLM finds → results are about the
  *lambda response curve* of a fixed operator, not absolute SOTA. Documented as a caveat.

## Success criteria
1. Driver runs end-to-end offline within seconds, emits a JSON sweep table.
2. The sweep shows a monotone/interpretable relationship: n_conditions decreases (weakly)
   as lambda grows; held-out accuracy has a sweet spot or degrades past some lambda.
3. `score_with_lambda(rs, ex, 0.003)` == `harness_synth.train_score(rs, ex)` (exact).
4. Tests pass.
