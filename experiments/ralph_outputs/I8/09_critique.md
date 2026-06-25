# 09 — Honest Critique

## What a reviewer would attack

1. **It's an essay, not an experiment.** The deliverable is theoretical; the "tests" validate
   *structure and grounding*, not the *truth* of the claims. A skeptical AAAI reviewer would say the
   comparison is only as good as its sourcing, and I cite no page numbers or quotes — just paradigm
   lineage. Mitigation present (qualitative claims, attributed repo numbers), but it is not a
   literature survey.

2. **Home-field bias risk remains.** Despite the "not a scorecard" caveat and the explicit
   "where code-as-policy LOSES" section, the doc is written *from inside* a code-as-policy repo, and
   the verifiability/safety/interpretability axes happen to be where that approach shines. A critic
   could argue the *choice of axes* is itself biased — e.g. there's no "open-domain generalization"
   or "handles unverifiable values" axis as a first-class row (it's relegated to the limits section).
   That is a fair hit.

3. **RLHF/CAI treated at a coarse grain.** Real RLHF/CAI have many variants (DPO, RLAIF flavors,
   process reward models, rule-based rewards) the doc collapses. Accurate at the canonical level,
   but a specialist would want the taxonomy.

4. **The matrix is editorial, not derived.** `axes_matrix.json` encodes my judgments; the validator
   checks it's well-formed and grounded, not that the *content* is correct. There is no external
   ground truth for "CAI interpretability = mixed."

5. **Frozen-model ceiling number is repo-internal and unaudited here.** I attribute ~0.86 to
   `ARCHITECTURE.md`, but I did not re-run `rex/frontier.py` to reproduce it (it needs `HUD_API_KEY`
   + live model calls — out of scope for a theory task). So that single quantitative anchor is
   *cited*, not *reproduced* in this task.

## What's genuinely solid
- The three paradigms are characterized correctly at the canonical level (RLHF: RM+PPO+KL;
  CAI: SL-CAI + RLAIF; code-as-policy: verifier-guided search + rejection gate over a frozen model).
- The "knowledge substrate" unifying frame is a legitimate, non-trivial lens.
- The honesty is real: the doc concedes code-as-policy's hard dependence on a verifier and its
  inability to exceed the model ceiling.
- The validator is non-vacuous (negative self-tests prove it rejects bad input).

## Net
A correct, well-grounded, honestly-bounded theoretical comparison with a checkable structured
artifact. Its main weakness is inherent to the task type (it's argued, not measured) and a residual
axis-selection bias that the limits section only partly neutralizes.
