# 05 — Ouroboros (3 engineers critique the spec, in sequence)

## Engineer A — correctness of the override
**Problem found:** The spec claims `score_with_lambda == train_score` at default lambda,
but `train_score` uses `confusion(ruleset, train_ex)` which depends on `is_safe_synth`'s
"first matching BLOCK rule wins" semantics. If my driver's confusion path diverged at all
(e.g. I re-implemented confusion), the equality could pass on `[]` but fail on a non-trivial
rule-set. **Fix:** the driver imports `confusion` directly from `harness_synth` (does NOT
re-implement it), and the equality test covers BOTH `[]` and a 2-rule set. Verified.

**Problem found 2:** `validate_ruleset` may *reorder* or rewrite rules (truncates reason to
160 chars, coerces `block`). If `propose` returns validated rules but the equality test uses
unvalidated rules, n_conditions could differ. **Fix:** the fidelity test uses the same rule
objects for both functions; n_conditions counts `r["conditions"]` identically in both. Not
an issue because conditions aren't altered by validate. Noted.

## Engineer B — does the offline operator actually exercise lambda?
**Problem found:** Greedy add-only with `stop_at=1.0` and a stalling propose means once the
operator stalls, every subsequent thompson node is a duplicate of the parent → the tree fills
with identical rule-sets and `best` is whichever. That's fine for `best`, but `node_rewards`
will show a flat tail that a reader might misread as "converged well" when it's actually
"stalled". **Fix:** documented in 07/09 that a flat node_rewards tail at high lambda means
*stalled*, not *converged*. The headline metric is `best` rule-set, which is correct.

**Problem found 2:** Add-only greedy can never *remove* a condition, so it cannot model the
case where a high lambda would prefer a *different smaller* rule over a subset of a big rule.
It only models "add fewer". This under-states how aggressively a real optimizer would simplify.
**Decision:** acceptable and disclosed — the task is the lambda response of the synthesis
*search*, and harness_synth's own search is also incremental (LLM edits a parent). Add-only is
a faithful-enough analogue. Disclosed in 09.

## Engineer C — scope / over-claiming
**Problem found:** The offline operator finds only ~3 rules vs haiku's 10, and its held-out
accuracy (0.744) is *below* both the hand-written baseline (0.949) and the real synthesized
harness (0.872 from the committed run). A reader skimming the table could conclude "synthesis
is bad" — wrong; that's the toy operator. **Fix:** every doc states the offline operator is a
weaker stand-in and reports the committed real haiku numbers (acc 0.861 train / 0.872 heldout)
from `rex/runs/harness_synth.json` as the reference point for what the real system does at the
default lambda. The sweep's value is the SHAPE of the response, not absolute accuracy.

**Problem found 2:** The lambda grid top (0.2) collapses to empty — but is 0.2 even reachable
in practice? The default is 0.003. **Decision:** keep the wide grid precisely to find the
collapse threshold; that's the safety-relevant finding (PSRE/DevOps). Disclosed.

## Final filtered spec (deltas)
- Import `confusion` (don't re-implement) — locks the fidelity equality. ✅ (already so)
- Fidelity test covers `[]` and a non-trivial rule-set. ✅
- Docs label operator on every result and cite the committed real numbers as reference. ✅
- Disclose: add-only greedy, flat node_rewards tail = stalled, single deterministic operator. ✅
