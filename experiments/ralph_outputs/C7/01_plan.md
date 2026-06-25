# C7 — Plan: Harness transfer (synthesize on simple, evaluate on cascade)

## Objective
Measure **cross-type transfer** of the AutoHarness-synthesized safety rule-set. We
synthesize the structured safety rules on the **simple** incident family only, then
evaluate `is_safe`-style classification accuracy on a held-out **cascade** family that
the synthesizer never saw. We report the **transfer gap**: in-family (simple) accuracy
minus cross-family (cascade) accuracy, against the hand-written `is_safe` baseline.

This is a stricter generalization test than `rex/harness_synth.py`'s default split (which
mixes simple+cascade in TRAIN and holds out a same-distribution mix). C7 deliberately
holds out an entire structurally-different family.

## Grounding
- `rex/harness_synth.py` — the synthesis machinery: `labeled_examples`, `features`,
  `is_safe_synth` (trusted interpreter over DATA rules), `train_score`, `propose_ruleset`
  (haiku mutation operator), `confusion`, `confusion_pred`, `handwritten_pred`.
- `rex/tree.py:thompson_search` — the Thompson-sampling tree search driver.
- `rex/harness.py:scenarios_by_family()` — gives `{'simple':[...12], 'cascade':[...20], 'novel':[...10]}`.

## Approach
1. New task-namespaced script `artifacts/transfer_simple_to_cascade.py` that IMPORTS the
   core functions (does not edit them). It overrides only the TRAIN / HELDOUT splits:
   TRAIN = all `simple` incidents, HELDOUT = all `cascade` incidents.
2. Run `thompson_search(propose, evaluate, budget)` over TRAIN(simple) labels only — no
   cascade label ever touches synthesis (leakage check enforced).
3. Score THREE harnesses (seed-empty, synthesized, hand-written `is_safe`) on both TRAIN
   (simple) and HELDOUT (cascade); compute accuracy, false-allow count/rate.
4. Define transfer gap per harness = `train_accuracy - heldout_accuracy`. Compare the
   synthesized harness's gap to the hand-written baseline's gap (the baseline is the
   ceiling: it generalizes by construction, so its gap is the irreducible distribution
   shift; the synthesized gap minus baseline gap = the *synthesis-induced* transfer cost).
5. Dump `result.json`-style numbers + hazard coverage to `artifacts/transfer_result.json`.

## Files to create
- `artifacts/transfer_simple_to_cascade.py` (runnable harness; imports core, edits nothing).
- `artifacts/transfer_result.json` (real numbers from the run).
- step files 01..10 + SUMMARY.md + result.json.

## Dependencies / risks
- LLM `agent.llm.call` for the haiku mutation operator needs an API key (loaded via
  `set -a; source ~/.zshrc`). RISK: no credits / rate limit → synthesis degrades to the
  seed (empty rule-set). MITIGATION: the search is robust to that (empty ruleset is a valid
  node); we still get hand-written baseline numbers and a *floor* synthesized result. We
  report whichever happens honestly.
- COMPUTE CAP ~15 min → keep BUDGET small (6–8 tree nodes, matching the core default of 8).
- Cascade incidents are mostly the `treats_forbidden_category` hazard; simple incidents
  carry more state-conditional hazards (leak_restart, last_ready_node, replica_limit,
  rollback_no_deploy). EXPECTED: the simple→cascade direction generalizes *well* for the
  forbidden-category rule (it appears in both families) but the synthesizer may never see
  some hazards that don't occur in cascade — those are out-of-scope, reported as such.

## Success criteria
- Real numbers for all 3 harnesses on simple(train) and cascade(heldout).
- A computed transfer gap with the hand-written baseline as reference.
- Leakage check passes (train/heldout disjoint, cascade labels untouched in synthesis).
- Artifact is runnable and syntax/parse-valid; result.json written.
