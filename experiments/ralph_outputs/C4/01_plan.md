# C4 — 01 Plan

## Objective
Analyze the **3 synthesized safety rules** produced by the AutoHarness-style search
(`rex/hud_harness_synth.py` -> `rex/runs/harness_synth_v2.json`) and answer: **are they
interpretable?** Deliver a clear interpretability report — for each rule: what it does, why
it helps, its failure modes, and a worked example — plus an overall verdict.

## Where the rules live (ground truth, read in full)
- `rex/harness_synth.py` — the synthesis machinery: feature extraction (`features`),
  trusted interpreter (`is_safe_synth`, `_rule_matches`), scoring (`train_score`,
  `confusion`), the haiku mutation operator (`propose_ruleset`, `_SCHEMA`).
- `rex/harness.py` — the **hand-written** baseline `is_safe` (Layer 1 category block +
  Layer 2 state-conditional traps) and `TOOL_TREATS` (tool -> category map).
- `rex/runs/harness_synth_v2.json` — the **3-rule** synthesized artifact (n_rules=3). This is
  the canonical "3 synthesized rules". (`harness_synth.json` is v1: a 10-rule over-conditioned
  predecessor; I document the v1->v2 collapse as evidence of interpretability pressure.)

## The 3 rules (verbatim from v2)
1. `block if treats_forbidden_category == True` (any tool) — "action treats a ruled-out cause".
2. `block if tool in {clear_cache,restart_pod,restart_service,scale_deployment} and leak_active == True` — "act while a leak is still uncapped".
3. `block if tool == rollback_deployment and rollback_without_deploy == True` — "rollback with no prior deploy".

## Approach
1. Confirm the rules by reading the JSON + the interpreter that executes them.
2. For each rule: map it back to the hand-written `is_safe` clause it recovered, explain the
   SRE intuition, enumerate failure modes (false-allow gaps, brittle `match_tools` lists),
   and construct a concrete worked example (incident -> features -> verdict).
3. Quantify: held-out accuracy 0.897 (synth v2) vs 0.949 (hand-written) vs 0.667 (empty seed);
   classify the 4 held-out false-allows (2 UNSEEN-in-train, 2 unlearnable).
4. Write the markdown report as the primary artifact; add a small runnable validator that
   re-applies the 3 rules through the real interpreter and reproduces the held-out numbers.

## Files to create (task-namespaced — NO edits to shared core)
- `experiments/ralph_outputs/C4/artifacts/rule_interpretability.md` — the report (primary).
- `experiments/ralph_outputs/C4/artifacts/validate_rules.py` — re-applies the 3 rules via
  `is_safe_synth` to held-out labels; prints the confusion + worked examples. Read-only import
  of `rex.harness_synth`; writes nothing to core.
- The 10 step files + SUMMARY.md + result.json.

## Dependencies
`rex.harness_synth`, `rex.harness` (import only). No LLM call, no cluster, no network — the
rules already exist as data, so this is a pure analysis task.

## Risks
- **Ambiguity in "3 rules":** v1 (`harness_synth.json`) has 10 rules; v2 has 3. Resolve by
  treating v2 as canonical (its `n_rules:3` is explicit and it is the improved run) and noting
  v1 as the over-conditioned predecessor. State this explicitly.
- **Interpreter import side effects:** `rex.harness` runs `_merge_generated_registry()` at
  import. It only reads files; safe. Validator must not call `main()` (which writes core JSON).

## Success criteria
- All 3 rules explained with what/why/failure-mode/worked-example, grounded in actual code.
- Validator runs and reproduces held-out accuracy 0.897 / 4 false-allows from the JSON.
- Honest verdict on interpretability incl. the brittle `match_tools` enumeration weakness.
