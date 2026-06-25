# 09 — Honest Critique

## What a reviewer attacks first
1. **The headline sweep uses a TOY operator, not the real haiku synthesis.** The biggest
   limitation. Because Anthropic billing is exhausted, I could not run the real
   `propose_ruleset` operator across lambdas. The offline greedy operator finds 3 rules where
   haiku finds 10, and its absolute held-out accuracy (0.744) sits *below* both the
   hand-written baseline (0.949) and the committed real synthesis (0.872). So the offline
   numbers characterize the *lambda sensitivity of a weaker search*, not the production system.
   I disclose this everywhere, but it is a real gap: the precise lambda thresholds (0.03 for
   first under-fit, 0.08 for collapse) would shift for the stronger operator.

2. **Add-only greedy can't model true simplification.** The offline operator only ever *adds*
   atoms; it can't replace a big rule with a smaller different one. A real optimizer under high
   lambda might keep ONE broad `treats_forbidden_category` rule (high coverage, one condition)
   rather than collapsing to empty. So my "collapse to empty at lambda≥0.08" is partly an
   artifact of add-only greedy: with no rule yet, no single atom beats its condition cost, so
   nothing is ever added. The *direction* (more lambda → fewer conditions → more false-allows)
   is robust; the exact collapse value is operator-specific.

3. **Single deterministic run = no variance bars.** For the offline operator this is fine (it's
   deterministic), but it means I have zero evidence about how the *stochastic* haiku operator's
   lambda response would vary across seeds. The interesting scientific question (does lambda buy
   held-out generalization for the REAL system?) remains unanswered — only scaffolded.

4. **Held-out generalization claim is weak here.** At the default lambda (0.003) the offline
   operator's held-out accuracy equals its lambda-0 accuracy — i.e. for THIS operator the penalty
   is a pure no-op tie-breaker, which is consistent with the core's design intent but means the
   sweep does not *demonstrate* a generalization benefit from lambda; it demonstrates the cost of
   too-LARGE lambda. The "lambda helps generalize" hypothesis is neither confirmed nor refuted
   for the real operator.

## What's genuinely solid
- The override mechanism is clean and *proven* equal to the core reward at the default lambda
  (the fidelity test). The sweep is anchored to the real `train_score`, not a guess.
- Real labels, real confusion matrices, real hand-written baseline — reproducible.
- The safety-relevant finding (a too-large complexity penalty silently disables the harness →
  all should-block actions become false-allows) is real and matters to the SRE story.
- No core files touched; core tests stay green.

## Honest bottom line
Completed deliverable: a runnable, tested, no-core-edit lambda-sweep driver + a real
deterministic sweep showing the lambda response curve and the collapse threshold, with the
real-haiku sweep scaffolded but BLOCKED by Anthropic billing. The absolute generalization
question for the production operator is unanswered pending API credit.
