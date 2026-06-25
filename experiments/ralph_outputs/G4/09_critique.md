# 09 — Honest Critique

## What a reviewer attacks first
1. **"Your taxonomy is one anti-pattern repeated."** 48/51 traps are `scale_deployment`.
   This is the strongest attack and it lands. The mitigation in the report (call it a
   "labeling scheme + seed taxonomy," surface the distribution honestly) reduces but does
   not eliminate it. The *scheme* is novel; the *taxonomic breadth* is thin. An honest paper
   would either broaden traps before claiming "taxonomy" or rename the contribution.

2. **"This is just a reward shaping constant."** Mechanically the trap term is an indicator ×
   0.60. A skeptic says that's trivial. The defense is the *conditioning* (same action flips
   label by mechanism) and the *coupled NL feedback*, not the scalar — but a hostile reviewer
   may not grant that the conditioning is deep when 48/51 share a tool.

3. **Evidence asymmetry.** We grounded our side in code but the competitor side in
   papers/docs. If SREGym or ITBench ship an undocumented unsafe-action list, the "none of
   them have this" claim weakens. The report dates and scopes the claim, which is the right
   move, but it remains a genuine epistemic gap.

4. **No demonstrated effect.** We assert the penalty creates within-group spread and is a
   learning signal, but G4 ran no ablation showing it changes agent behavior vs a resolved-
   only oracle. The claim of *usefulness* is argued, not measured. (Correctly out of scope
   for a comparison task — but it is what makes or breaks the contribution.)

## What's weak in my own artifact
- `_const_assignments` and `load_why_table` are AST heuristics tied to the current shape of
  `scoring.py`; if that file is refactored (e.g. the why-table moved to a module constant or
  the weights split into separate assignments) the extractor silently degrades to `None`/`{}`
  rather than failing loudly. Tests would catch the constant case but not a moved why-table.
- The wildcard-target false-positive risk (`target: None`) is documented but not quantified;
  I did not check how many multi-node scenarios could mis-flag a legitimate scale.

## Net honest assessment
A solid, real, grounded comparison with a correctly *scoped* novelty claim and a re-runnable
data artifact. The contribution is genuine but **narrow and currently shallow**: a clean
labeling scheme that competitors lack, undercut by tool monoculture and the absence of a
behavior-change measurement. "Completed deliverable, modest-but-real contribution" is the
fair verdict — not a headline result.
