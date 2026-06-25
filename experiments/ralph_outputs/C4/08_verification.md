# C4 — 08 Verification

## Success criteria (from 01) vs. actual

| Criterion | Met? | Evidence |
|---|---|---|
| All 3 rules explained: what / why / failure-mode / worked-example | YES | `rule_interpretability.md` "Per-rule analysis" — R1, R2, R3 each have all four. |
| Grounded in the actual synthesized rules (not invented) | YES | Rules quoted verbatim from `rex/runs/harness_synth_v2.json`; verbs ("recovers/broadens") cross-checked against `rex/harness.py:is_safe`. |
| Validator runs and reproduces published held-out numbers | YES | `validate_rules.py` exit 0; acc 0.897, FA 4, FB 0 — matches JSON `heldout_table`. |
| Honest interpretability verdict incl. weaknesses | YES | TL;DR verdict + "Failure modes" + "Honest limitations" sections; `match_tools` brittleness and the 0.897-vs-0.949 gap stated. |
| No shared core files edited | YES | Only files under `experiments/ralph_outputs/C4/`; validator imports read-only, never calls `main()`. |

## Are the outputs real (not placeholder)?
- The report's every quantitative claim is reproduced by running `validate_rules.py` against the
  real interpreter `rex.harness_synth.is_safe_synth` — not transcribed by hand.
- Worked examples are **actual** `is_safe_synth` verdicts on real held-out labeled examples
  (`cpu_saturation_leaf / cordon_node`, etc.), printed by the validator.
- The v1 (10-rule) vs v2 (3-rule) comparison uses both real run files
  (`harness_synth.json`, `harness_synth_v2.json`).

## Independent sanity checks
- `n_rules` field in the JSON == 3 == `len(rules)` loaded == count explained. Consistent.
- Held-out false-allow detail in the report matches the JSON's `heldout_misses_synth_v2.detail`
  (same 4 actions, same hazard labels) — verified by the validator printing them from the live
  confusion, independent of the JSON's stored list.

## Verdict
**Verified.** The deliverable answers the task question ("are the 3 synthesized rules
interpretable?") with a defensible YES, grounded in code, with numbers reproduced by a runnable
artifact, and with weaknesses stated honestly.
