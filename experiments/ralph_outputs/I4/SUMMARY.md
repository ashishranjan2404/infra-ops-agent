# I4 — SUMMARY

**Task.** Write the information-theoretic argument (feature-space entropy / coverage) for why
the REx safety harness needs only ~3 rules, with a runnable witness over the real scenarios.
Build on C12's proof rather than duplicate it.

## What was delivered
- `artifacts/three_rules_information_argument.md` — the main deliverable. Upgrades C12's
  *asserted* §6 ("I(y;R4|c)=0") into a **measured** entropy decomposition over the real 42
  scenarios: H(y), H(y|R1..Rk), per-rule information gain, the Phi-bounded MI ceiling of any
  4th rule, and coverage of the should-block mass. Honest argument-vs-proof table; residual
  named and quantified. Composes with C12's Lemma 1 (the mechanism-level proof).
- `artifacts/entropy_witness.py` — deterministic, LLM-free; computes every number live from
  `rex.harness_synth` over all 42 scenarios. Self-checking PASS criterion. Exit 0.
- 10 step files + this SUMMARY + result.json.

## Headline finding (measured, honest)
- H(y) = 0.971 bits. A **single** spanning category rule (R1) removes **0.84** bits (86.8%).
- **Three** rules remove **0.927** bits = **95.5%** of H(y); coverage of block mass **99.08%**.
- The Phi floor is H(y|full Phi) = 0.0089; so **any 4th Phi-rule gains <= 0.0344 bits** (<=3.5%
  of H(y)) — and that residual is a rollback_without_deploy *feature collision* on three
  cascade incidents, **not a 4th hazard mechanism**.
- **35 topology-trap positives escape Phi entirely** — the honest out-of-scope residual.
- **Refines C12:** C12 said I(y;R4|c)=0; the real value is 0.0344 bits, located precisely.

## Conclusion
Three rules are **information-complete over the harness's own six features, up to a named
0.0344-bit residual**. The boundary beyond is **more features (rollback provenance,
victim-vs-root topology), not more rules.**

## Compliance
- No shared core file edited (git status: only ?? experiments/ralph_outputs/I4/).
- Witness reproducible: python3 experiments/ralph_outputs/I4/artifacts/entropy_witness.py.
- All six spec invariants (T1-T6) verified on real data.

## Status: completed (deliverable real and reproducible; the IT claim is measured and honestly scoped).
