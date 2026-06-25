# C2 — Plan: harness synthesis on cascade incidents only

## Objective
Run the AutoHarness-style rule-synthesis (Thompson-tree over LLM-proposed *data*
rules, scored by classification accuracy on incident labels) using **only cascade
incidents**, and ask: does it discover a **different** rule-set than (a) the baseline
mixed-family synthesis run and (b) the conceptual hand-written rule set?

## Background / grounding
- `rex/harness_synth.py` is the synthesis engine. It:
  - extracts 6 boolean/string FEATURES per (tool,target,incident) example,
  - labels each via `ground_truth()` (block/allow + a hazard tag) from the spec,
  - searches rule-sets with `rex/tree.py:thompson_search` (LLM = mutation operator),
  - scores with `train_score` (2x penalty on dangerous false-allows + tiny
    complexity penalty), and reports TRAIN vs HELD-OUT confusion for 3 harnesses
    (empty seed, synthesized, hand-written `is_safe`).
- Baseline split (`TRAIN`/`HELDOUT` in harness_synth.py) is **mixed**: leaf incidents
  (oom_kill, bad_deploy_leaf, cpu_saturation_leaf, singleton_node_notready) +
  cascades (gcp_service_control, aws_dynamodb_dns, cloudflare_waf, crowdstrike_bsod,
  railway_gcp_suspension, azure_ddos).
- `scenarios_by_family()` exposes a `cascade` family of **20** incidents (6 hand-authored
  + 14 merged from the generated registry).

## Hypothesis
Cascade incidents exhibit a different hazard mix than leaf/node incidents. Leaf-only
hazards `leak_restart`, `last_ready_node`, `replica_limit` should be **absent** from a
cascade-only set, so cascade-only synthesis should NOT learn rules guarding those
hazards. It should concentrate on `treats_forbidden_category` (treating a ruled-out
cause — the canonical "loud victim != root" cascade failure mode), `trap_action`, and
`rollback_no_deploy`. => a *narrower / different* rule-set than the baseline.

## Approach
1. Compute the cascade family via `scenarios_by_family()`; fix a 14-train / 6-held-out
   cascade split (held-out spans every cascade hazard so generalization is testable).
2. Reuse ALL baseline machinery (features, labels, interpreter, scoring, search) so the
   only changed variable is the incident split + the mutation model.
3. Mutation model: Anthropic is out of credits (400) -> route to the HUD gateway
   (`deepseek-v4-pro`). REx diversity comes from per-node feedback, not temperature.
4. Run synthesis (budget 8), dump `cascade_synth.json`.
5. Compare the cascade-only rule-set vs the baseline `rex/runs/harness_synth.json`
   rule-set and vs the hand-written `is_safe` conceptual rules.

## Files
- NEW (task-namespaced): `artifacts/cascade_synth.py`, `artifacts/cascade_synth.json`,
  `artifacts/compare.md`.
- READ-ONLY: `rex/harness_synth.py`, `rex/harness.py`, `rex/tree.py`, `rex/runs/harness_synth.json`.
- DO NOT edit any `rex/*.py` (real-artifact rule).

## Dependencies / risks
- LLM/network: gateway must be reachable (verified: deepseek-v4-pro returns "OK").
- Non-determinism: LLM proposals vary run-to-run; the *structure* of the discovered
  rules (which features/tools they guard) is the stable signal, not exact JSON.
- Compute cap ~15 min: budget 8 nodes x 1 gateway call each ≈ well under cap.

## Success criteria
- A real cascade-only synthesis run completes and writes a valid JSON artifact.
- A concrete, evidenced comparison: which rules differ, which hazards each set guards,
  and held-out accuracy of cascade-synth vs hand-written on the cascade held-out set.
- Honest reporting if cascade-synth generalizes worse than the mixed baseline.
