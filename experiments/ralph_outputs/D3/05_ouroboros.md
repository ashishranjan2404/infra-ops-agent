# D3 — 05 Ouroboros (self-critique as 3 different engineers)

## Pass 1 — Distributed-systems engineer (correctness of the key resolver)
**Problem found.** `_default_key` falls back to `repr(rollout)` for objects with no scenario
field. Two *different* rollouts of the same scenario that lack any id field would then land in
DIFFERENT groups (distinct reprs), silently re-introducing cross-scenario-style fragmentation —
the exact bug we claim to fix, but inverted (over-splitting). 
**Resolution.** Documented: the resolver tries 6 concrete attributes first; `repr` is a last
resort only. Real HUD `Run` objects expose `.task` (→ `.task.id`), which is hit before `repr`.
The test `_Run` carries `.task_id`. Acceptable: the fallback is a safety net, not the path.
Left a note that callers SHOULD pass an explicit `key=` for exotic rollout types.

## Pass 2 — Statistician (is the variance claim actually about gradient variance?)
**Problem found.** `E[A^2]` is the advantage second moment, NOT literally `Var(∇)`. The real
policy-gradient variance is `Var(A·∇logπ)`, which also depends on `∇logπ`. Claiming "reduces
gradient variance" from `E[A^2]` alone is an over-statement if `∇logπ` correlates with the
between-scenario term.
**Resolution.** Tightened the wording to "a proxy upper bound on the per-sample gradient
variance, holding `∇logπ` fixed across the two baselining schemes." Since both schemes use the
SAME rollouts (same `∇logπ`), the only thing that changes is `A`, so the comparison `E[A^2]_mixed`
vs `E[A^2]_same` is apples-to-apples for the advantage's contribution. The decomposition
(`between + within`) is exact. Honest and defensible.

## Pass 3 — Pragmatic RL engineer (does the driver actually preserve the invariant end-to-end?)
**Problem found.** The driver concatenates per-scenario sub-batches then calls ONE
`trainer.step(batch, group_size=G)`. If HUD's `trainer.step` re-chunks `batch` into groups of G
by POSITION, the invariant holds ONLY if every scenario contributes exactly G rollouts and they
stay contiguous. If `ts_i.run(group=G)` ever returns ≠ G rollouts (a timeout/error drops one),
the positional chunking would straddle a scenario boundary — silently mixing again.
**Resolution.** This is a real edge. Mitigations applied/documented:
(a) the driver collects each scenario's runs as a contiguous block appended in order, so under
nominal G-per-scenario returns the chunking is clean;
(b) added a `group_rollouts_by_scenario(batch)` sanity grouping + assert before `trainer.step`
to make the invariant inspectable;
(c) documented in 09 that the *robust* form is to call `trainer.step` once PER scenario sub-batch
(a per-scenario optimizer micro-step) if HUD chunks positionally and ragged returns occur — left
as a one-line switch for the maintainer since it depends on HUD's exact `step` contract, which
needs the live trainer to confirm.

## Final filtered spec changes
- Key resolver: 6 explicit attrs before `repr`; recommend explicit `key=` for exotic types.
- Variance claim reworded to "proxy upper bound, `∇logπ` held fixed"; decomposition is exact.
- Driver: contiguous per-scenario blocks + pre-step sanity grouping; documented robust per-scenario
  `trainer.step` fallback for ragged returns (pending live HUD `step` semantics).
