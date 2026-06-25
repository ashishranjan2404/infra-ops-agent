# 01 — Plan: C11 Rule-Ablation of the safety harness

## Objective
Quantify each safety RULE's marginal contribution to the hand-written gate
`rex/harness.py:is_safe` by disabling one rule at a time and measuring the
`is_safe`-classification accuracy drop on a fixed labeled action set.

## What "the 3 rules" are (grounded in rex/harness.py:is_safe)
`is_safe` is a disjunction of independent guards. Three of them actually FIRE as
blocks across the scenario set (verified empirically before planning):
- **R1 forbidden_category** (Layer 1): an action whose `TOOL_TREATS[tool]` category is
  in the incident's `forbidden_categories` is blocked (treats a ruled-out cause).
- **R2 leak_restart** (Layer 2): `restart_pod`/`restart_service` while a mem leak is active.
- **R3 last_ready_node** (Layer 2): `drain_node`/`cordon_node` on the last Ready node.
Two further minor guards (R4 replica_limit, R5 rollback_no_deploy) are reported for
completeness — R4 never fires in the current scenario set.

## Approach
- Labels = spec-derived `should_block` from `rex/harness_synth.py:labeled_examples`
  (independent of any harness) — same yardstick the synthesis experiment uses.
- Ablate rule R via a WRAPPER: call the real `is_safe`; each guard returns a distinct,
  stable `reason` string, so if `is_safe` blocked *because of R*, override to ALLOW.
  Exactly one rule is removed; all other guards keep firing through the real code path.
- Run over ALL registered scenarios (~42), report full accuracy, per-rule ablated
  accuracy, accuracy drop, and false-allows introduced (the safety-critical metric).

## Files to create (task-namespaced, NO core edits)
- `artifacts/rule_ablation.py` — the ablation harness (wrapper + scorer + CLI).
- `artifacts/test_rule_ablation.py` — hermetic tests for the wrapper.
- `artifacts/ablation_result.json` — the produced numbers.

## Dependencies
`rex.harness` (is_safe, load_scenario, _SCENARIOS), `rex.harness_synth.labeled_examples`.
No network, no LLM (labels are deterministic spec-derived).

## Risks
- Reason-string matching is brittle if `is_safe` reason text changes (mitigation: tests
  assert each guard's reason matches exactly one rule predicate).
- "First matching block-rule wins" in `is_safe` means a rule masked by an earlier rule
  shows a smaller drop than its standalone value — documented as a known property.

## Success criteria
- Real per-rule accuracy-drop table over ≥40 scenarios, no fabricated numbers.
- Tests pass. Full harness accuracy ≥ every ablated accuracy (each rule net-helpful).
