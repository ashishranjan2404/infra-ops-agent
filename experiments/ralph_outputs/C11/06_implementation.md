# 06 — Implementation

## Artifacts built (all under experiments/ralph_outputs/C11/artifacts/, NO core edits)
- **`rule_ablation.py`** — the ablation harness:
  - `RULES`: 5 rule predicates over `is_safe` reason strings; `HEADLINE` = R1/R2/R3.
  - `_state_for(e)`: rebuilds the exact state dict `is_safe` reads, from the scenario
    (mirrors `rex.harness.build_state` non-engine fields; mem_leak_active equivalence
    documented inline).
  - `predict_block(e, disabled)`: calls the REAL `rex.harness.is_safe`; if it blocked
    *because of* `disabled` (reason matches the rule predicate), overrides to allow.
    Validates `disabled in RULES` up front (KeyError otherwise).
  - `confusion(...)`: tp/tn/false_allow/false_block/accuracy vs spec-derived
    `should_block` labels.
  - `main()`: CLI over all `_SCENARIOS` by default; fault-tolerant per-scenario load;
    prints a table and writes `ablation_result.json`.
- **`test_rule_ablation.py`** — 4 hermetic tests (no LLM/network).
- **`ablation_result.json`** — produced output (real numbers).

## How the ablation works (the key idea)
We never re-implement or mutate `is_safe`. Each guard inside `is_safe` returns a distinct,
stable `reason` string. To disable rule R we run the genuine `is_safe`; on a block whose
reason matches R's signature, we flip the decision to ALLOW. Every other guard fires
through the real code path. This is a true delete-one ablation via the production code.

## Labels
Ground truth = `should_block` from `rex.harness_synth.labeled_examples`, derived from each
scenario's SPEC (trap lists, forbidden categories, correct-fix exemptions, state-conditional
dangers) — independent of any harness. Accuracy = "does is_safe agree with the spec?"

## Core change proposed but NOT applied
No core change is needed for this task — the wrapper achieves ablation without touching
`rex/*.py`. (If one ever wanted ablation inside core, the clean form would be an optional
`disabled_rules: set[str]` parameter on `is_safe` with early `continue` per guard; this is
documented here as the proposed shape, NOT applied, per the parallel-safety rule.)

## Run command
```
python3 experiments/ralph_outputs/C11/artifacts/rule_ablation.py
```
