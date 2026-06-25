# A12 — 09 Critique (honest)

## What's weak
1. **Static prior, not measured difficulty.** The headline limitation. The score is a
   weighted sum of structural YAML fields, not empirical model pass-rate. A frozen
   LLM may find some "hard" cascades easy (seen in public postmortems) and some
   "easy" leaves hard (misleading metric). The *coarse* simple-vs-real split is
   trustworthy; the *fine* within-tier order is provisional.
2. **Hand-set weights.** `loud_not_cause=2.5`, `hidden=2.0`, etc. are reasoned but
   uncalibrated. A reviewer will (correctly) ask for a correlation against pass@k.
   Mitigated only by exposing the full feature vector + weight dict for re-tuning.
3. **Heavy ties.** Within the hard tier many incidents share difficulty 15.5 or 17.0,
   so they're ordered alphabetically — effectively unordered inside a tie band. The
   feature vector lets a user break ties on a chosen sub-signal, but the default
   scalar doesn't.
4. **`buried_depth` weight (0.04) is nearly inert** — it rarely changes an ordering.
   Borderline cosmetic.
5. **Unknown-family incidents.** 17 newly-added leaf yamls aren't in `registry.json`
   yet, so they get `family="unknown"` and zero red-herring credit; their score may
   be slightly understated until the registry catches up.

## What a reviewer attacks first
- "Show me curriculum-order vs random-order vs anti-curriculum on the same model and
  prove the ordering matters." A12 ships the *ordering*, not that experiment — so
  this is the obvious unanswered question.
- "Your difficulty is circular — you defined hard as 'has the traits you call hard.'"
  True; it's a domain prior, defensible but not empirical.

## What's missing / future work
- Correlate `difficulty` against empirical pass@k via `rex/eval_pass_at_k.py` across
  the spanning model set, then refit weights (e.g. logistic regression of pass-rate on
  the feature vector). That converts the prior into a measured curriculum.
- Tie-breaking using a secondary empirical signal (REx refinement steps to solve).
- Buckets for anti-curriculum / mixed schedules (the data is present; just not emitted
  as named bands yet).

## Honesty note
Nothing here is fabricated: the ordering is regenerated from real specs and validated.
The negative I will not paper over is that "difficulty" is asserted from structure, not
demonstrated against a learner — that calibration is genuinely out of scope for A12 and
left as the explicit next step.
