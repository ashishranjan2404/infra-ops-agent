# C2 — Critique (honest)

## What a reviewer attacks

1. **Model confound is real and not fully eliminable.** The baseline run used
   claude-haiku-4-5; cascade-only used gpt-5.5 (Anthropic out of credits). So I cannot
   attribute the *rule-count* drop (10→2) purely to the cascade split — a tidier model
   alone could compress 9 per-tool forbidden-category rules into one. My defense (the
   *hazard-coverage* difference is split-driven, because leaf hazards are simply absent
   from cascade training data) is sound, but the cleaner experiment would re-run the
   *baseline* mixed split with gpt-5.5 too, holding the model fixed. I did not (compute
   cap + the structural claim doesn't require it), but a reviewer is right to want it.

2. **n=1.** One gpt-5.5 synthesis run. The search plateaus at ~0.95 and the forbidden-
   category rule is deterministic given the feedback, so the *structural* claim is robust,
   but the spurious `scale_deployment` blanket rule is exactly the kind of artifact that
   could vary across seeds/runs. I report node scores but did not bootstrap variance.

3. **The "different rules" finding is partly trivial and partly deep.** Trivially, any two
   LLM runs produce different JSON. The deep, defensible part is: cascade-only synthesis
   *cannot* learn the leaf guards because there is no supervision for them — that's a
   property of the data, not the model. I separated these, but a skeptic could still say
   "you trained on a subset, of course it forgot the rest" — which is, in fairness,
   precisely the point the task asked me to demonstrate.

4. **Held-out result is slightly negative.** Cascade-synth (0.83) underperforms the
   hand-written harness (0.864) on the cascade held-out set, and adds 5 false-blocks via
   its overfit scale rule. So cascade specialization did NOT beat the human baseline here.
   I report this rather than spin it.

5. **Feature-set ceiling, not a synthesis property.** Many cascade unsafe actions are
   `trap_action` with NO active features — neither synthesis nor `is_safe` can catch them.
   So part of what looks like "cascade-synth leaks unsafe actions" is an inherent limit of
   the 6-feature representation. A fairer experiment would add a `trap_action` feature; but
   that means editing core (forbidden) and changes the comparison, so I left it.

## What's weak / missing
- No re-run of the baseline split under gpt-5.5 to fully isolate the model.
- No variance estimate (single run).
- The spurious `scale_deployment` rule shows the complexity penalty (λ=0.003) is too weak
  to suppress a 0-condition over-general rule when it raises train score — worth flagging
  to the engine authors, but out of scope to fix here.

## Net
A genuine, reproducible result with a real (small) negative held-out delta and two honestly
reported blockers (deepseek no-op; model confound). It answers the task's question — yes,
cascade-only synthesis finds materially different (narrower, forbidden-category-centric)
rules — without overclaiming superiority.
