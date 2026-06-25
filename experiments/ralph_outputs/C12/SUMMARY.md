# C12 — SUMMARY

**Task.** Write a formal proof/argument (information-theoretic / VC-style) for why
3 rules suffice to cover the trap-action space of the REx safety harness.

## What was delivered
- `artifacts/three_rules_proof.md` — the main deliverable. Grounded in the real rules
  (`rex/harness.py:is_safe`, `TOOL_TREATS`; `rex/harness_synth.py:features`,
  `ground_truth`, `FEATURES`). Contains: assumptions A1–A5; **Lemma 1 (proven)** — the
  feature-expressible hazard space has exactly 3 mechanism classes (wrong-diagnosis /
  fault-masking / margin-destruction); **Proposition 2 (empirically verified)** — 3
  rules realize the block-label on 99.6% of the realized feature-expressible set; an
  **information-theoretic core** showing any 4th rule over the feature set Φ has
  I(y; R4 | c) = 0 (3 rules saturate Φ); an honest negative-result section; 4 limits.
- `artifacts/verify_three_rules.py` — runnable witness; enumerates the realized trap
  space over all 42 scenarios (580 examples) and reports the real numbers.

## Headline finding (honest, mixed)
- 3 feature-rules = 99.6% of the feature-expressible trap space (529/531).
- Full corpus: FAIL — 37 false-negatives are topology-dependent explicit trap_actions
  (scale/restart/failover a loud VICTIM), a hazard NOT in the 6 features; 2
  false-positives are a rollback_deployment feature collision (correct content rollback
  with no deploy event).
- Conclusion: 3 rules are information-theoretically complete FOR the fixed feature space
  the human harness chose — the boundary beyond it is more features (victim-vs-root
  topology), not more rules.

## Compliance
- 10 step files + this SUMMARY + result.json under experiments/ralph_outputs/C12/.
- No shared core file edited (git: only ?? experiments/ralph_outputs/C12/).
- Witness reproducible: python3 experiments/ralph_outputs/C12/artifacts/verify_three_rules.py

## Status: completed (deliverable real; the universal claim is honestly re-scoped, not faked).
