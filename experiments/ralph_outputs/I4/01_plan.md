# I4 — Plan: information-theoretic argument for 3-rules sufficiency

## Objective
Write a rigorous **information-theoretic** argument (feature-space entropy / coverage)
for why the REx safety harness needs only ~3 rules, with a **runnable witness** over the
real scenarios. Honest about where it is argument vs proof.

## Prior art — build on C12, do not duplicate
C12 (`experiments/ralph_outputs/C12/`) already produced:
- `three_rules_proof.md`: a VC-style / branch-enumeration argument. Its **Lemma 1**
  (the Φ-expressible hazard space has exactly 3 mechanism classes) is a real proof by
  exhaustion of `ground_truth`'s positive branches. Its §6 "information-theoretic
  restatement" *asserts* `H(y|c)≈0` and `I(y;R4|c)=0` but **does not compute them**.
- `verify_three_rules.py`: an accuracy/separability witness (mismatches, collisions),
  not an entropy computation.

**My distinct contribution (I4):** make the information-theoretic claim *quantitative*.
Actually compute, over the real realized feature space:
- `H(y)`, the base entropy of the block-label;
- `H(y|R1)`, `H(y|R1,R2)`, `H(y|R1,R2,R3)` — residual entropy after k rules;
- the per-rule **information gain** in bits;
- `I(y;R4|R1,R2,R3)` — does a 4th Φ-rule carry information? (C12 asserted 0; I measure it.)
- **coverage** of the should-block probability mass by the first k rules.

This tests C12's §6 assertion empirically. If it is exactly 0, I confirm C12 with numbers;
if not, I refine C12's overclaim honestly.

## Approach
1. Reuse pure-data helpers from `rex/harness_synth.py` (`labeled_examples`, `features`,
   `ground_truth`) and the 3 rule-schemas (same as C12, for comparability). No LLM path.
2. Enumerate the realized set V over all loadable scenarios.
3. Split into the Φ-expressible region (the human harness's own feature space) and the
   out-of-scope residual (topology traps that escape Φ) — report both honestly.
4. Compute entropy decomposition + coverage curve + conditional MI of a 4th rule.
5. Write the argument doc grounding every number in the witness output.

## Files to create (task-namespaced, no shared edits)
- `artifacts/entropy_witness.py` — the runnable computation.
- `artifacts/three_rules_information_argument.md` — the argument doc.
- 10 step files + SUMMARY.md + result.json.

## Dependencies
- `rex/harness.py`, `rex/harness_synth.py` (READ ONLY — imported, never edited).
- `scenarios/cidg/**` (42 scenarios via the registry merge).
- Python stdlib only (`math`, `collections`).

## Risks
- **Risk: I just rewrite C12.** Mitigation: my deliverable is the *measured* entropy
  decomposition + a test of C12's "I(y;R4|c)=0" claim — a genuinely new artifact.
- **Risk: the numbers contradict C12's "exactly 0".** That is a *feature*, not a bug —
  report it honestly; a measured small residual is more credible than an asserted 0.
- **Risk: confusing "argument" with "proof".** Mitigation: explicit honesty banner; the
  closed proof is C12's Lemma 1 (mechanism taxonomy); my entropy numbers are over the
  *realized* set (A5), not a worst-case bound.

## Success criteria
- Witness runs clean over the real 42 scenarios and prints real entropy/coverage numbers.
- The doc derives "3 rules suffice" from those numbers, scoped to Φ, with the residual
  named and quantified.
- No shared core file edited (git shows only `experiments/ralph_outputs/I4/`).
