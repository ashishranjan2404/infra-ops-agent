# C8 — 01 Plan: a 4th rule candidate, can we push past 89.7%?

## Objective
The synthesized safety harness (`rex/harness_synth.py`, v2 run) reaches **89.7%
accuracy on HELD-OUT incidents** with a 3-rule set. The hand-written `is_safe`
reaches 94.9%. Question: can a **4th candidate rule** close that gap — and is the gap
a *search* failure (the LLM mutation operator could have found it) or a *data* gap
(no training signal)? Report honestly; the rule may not help, or may "help" only by
being hand-injected.

## Grounding (read in full)
- `rex/harness_synth.py` — the synthesis: `FEATURES`, `is_safe_synth` (trusted
  DATA interpreter), `confusion`, `train_score`, `propose_ruleset` (haiku operator),
  TRAIN/HELDOUT split.
- `rex/harness.py` — `is_safe` (the human baseline) and `TOOL_TREATS`. Layer-2 has a
  `draining_last_ready_node` block the synthesized set lacks.
- `rex/runs/harness_synth_v2.json` — the 89.7% artifact (3 rules, held-out table).

## Key observation from the baseline artifact
The 3 synthesized rules cover: `treats_forbidden_category`, `leak_active`,
`rollback_without_deploy`. The `FEATURES` list also contains
**`last_ready_node_op`** and **`at_replica_limit`** — neither is used by any rule.
The v2 held-out misses are 4 false-allows:
- `singleton_node_notready` / drain_node + cordon_node → hazard `last_ready_node`
  (these have `last_ready_node_op==True`) — **learnable via the unused feature**
- `cpu_saturation_leaf` / clear_cache + restart_pod → hazard `trap_action`
  (no active feature) — **unlearnable; `is_safe` misses them too**

## Approach
1. Reproduce 89.7% deterministically (no LLM) from the saved v2 rules + real
   `confusion`/`labeled_examples`.
2. Define a **4th rule**: block drain/cordon when `last_ready_node_op==True`
   (mirrors `is_safe` Layer-2). Use ONLY the existing `last_ready_node_op` feature so
   it passes the synth's own `validate_ruleset`.
3. Evaluate 3-rule vs 4-rule on TRAIN / HELDOUT / ALL via `confusion` + `train_score`.
4. **Honesty probe:** count TRAIN examples with `last_ready_node_op==True`. If 0, the
   LLM search has no gradient → the rule is human-injected, not discovered.

## Files to create (task-namespaced; NO core edits)
- `artifacts/rule4_candidate.py` — harness (imports rex.harness_synth, no edits to it)
- `artifacts/test_rule4_candidate.py` — pytest
- `artifacts/rule4_result.json` — emitted report

## Dependencies / risks
- Depends on `rex/harness_synth.py` import working under python3.13 (it does; pure-py
  for the offline path — `agent.llm.call` only needed if we re-run search, which we
  do NOT).
- Risk: the rule "helps" held-out but has no train signal → must be reported as an
  OOD generalization gap, not a synthesis win. This is the core honesty point.
- Risk: a 4th rule might add false-blocks elsewhere. Must verify FB delta == 0.

## Success criteria
- Reproduce 89.7% exactly.
- 4-rule held-out accuracy **strictly > 0.897**, with **no new false-blocks**.
- Honest classification of WHY the search missed it (train signal count).
- Tests green; report JSON real.
