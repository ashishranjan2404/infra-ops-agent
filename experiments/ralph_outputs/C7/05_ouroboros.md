# C7 — Ouroboros: self-critique as 3 engineers

## Engineer A — "the interpreter/correctness hawk"
Problems found:
1. **A1.** `propose_ruleset(parent, train_ex)` expects `parent` to be the tree node dict
   (`parent_node["cand"]`), and the SEED parent is `None`. The `thompson_search` driver must pass
   the node object, not the cand. → Verified: core `harness_synth.main` uses the exact same
   `lambda parent: propose_ruleset(parent, train_ex)`. Safe — I mirror it verbatim.
2. **A2.** `confusion_pred(handwritten_pred, exs)` calls `handwritten_pred(e)` which calls
   `load_scenario(e["incident"])` and `is_safe(...)` for EVERY example — that's 20 cascade × ~13 =
   ~260 scenario loads. Each `load_scenario` parses YAML. Could be slow-ish but well under 15 min
   (no LLM). Acceptable; note it.
3. **A3.** If `labeled_examples` raises for any generated cascade scenario (missing spec field),
   the whole run dies. → Mitigation: wrap per-incident label building in try/except, skip + record
   any incident that fails to load, so one bad generated YAML doesn't sink the experiment.

## Engineer B — "the metrics skeptic"
Problems found:
1. **B1.** Comparing `accuracy_train - accuracy_heldout` across families is only meaningful if the
   block/allow base rates are comparable. If cascade is 90% block and simple is 50% block, the
   seed-empty harness (allows all) has very different accuracy by base rate alone. → FIX: report
   per-family base rate (block fraction) in the result so the gap is interpretable. Add
   `block_rate_train` / `block_rate_heldout`.
2. **B2.** `false_allow_rate` is `false_allow / (tp+false_allow)` = false-allow over *blockable*
   examples. Good — that's recall-complement on the danger class, the right denominator. Keep.
3. **B3.** The "synthesis_cost = gap(synth) - gap(oracle)" can be negative if synth happens to
   generalize *better* on accuracy than the oracle on this particular label set (possible if synth
   over-blocks in a way that helps cascade base rate). Don't over-claim; report raw gaps and let
   the confusion matrix carry the nuance. → Accepted: keep `synthesis_cost` but caveat it in prose.

## Engineer C — "the scope/over-engineering critic"
Problems found:
1. **C1.** Do we need the seed-empty harness in the table? YES — it's the floor that makes the
   false-allow rate of an "allow-everything" policy explicit, and it's the fallback if synthesis
   fails. Keep.
2. **C2.** `test_handwritten_oracle_strong` asserting ≥0.8 is brittle if some generated cascade
   scenario has weird forbidden categories. → Soften to ≥0.7 and make it a sanity bound, not a
   tight contract. Better: assert hand-written cascade accuracy ≥ seed-empty cascade accuracy
   (oracle must beat allow-all) — that's the real invariant.
3. **C3.** Saving full `false_block_ex`/`false_allow_ex` (which embed feature dicts) bloats the
   JSON. → Save only compact `(incident, tool, target, hazard)` tuples (matches core's dump style).

## Final filtered spec deltas
- Add per-incident try/except in label building; record `skipped_incidents`.  (A3)
- Add `block_rate_train` / `block_rate_heldout` to the result.  (B1)
- Report raw gaps; caveat `synthesis_cost` sign in prose.  (B3)
- Oracle test invariant: hand-written cascade accuracy ≥ seed-empty cascade accuracy.  (C2)
- Compact false-allow/false-block dumps only.  (C3)
- Everything else from 04_spec.md stands.
