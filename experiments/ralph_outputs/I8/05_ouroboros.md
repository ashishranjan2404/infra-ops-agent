# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the pedant on definitions"
Problems found:
1. **CAI conflation.** Constitutional AI is *two* stages — supervised (SL-CAI: model critiques and
   revises its own responses against principles) AND RL (RLAIF: a preference model trained on
   AI-generated comparisons drives PPO). A draft that says "CAI = RLHF with AI labels" is wrong: the
   supervised self-revision stage is a distinct contribution. → Fix: describe both stages.
2. **RLHF KL term omitted.** Any rigorous RLHF description must mention the **KL penalty to the
   reference (SFT) policy** — without it PPO collapses / reward-hacks. Omitting it is a tell of
   shallow understanding. → Fix: include it.
3. **"frozen model" overclaim.** The doc must not imply code-as-policy is model-*independent* in
   quality — it inherits the frozen model's ceiling (haiku+REx tops out at the solvable set, can't
   exceed what the model+verifier can reach). → Fix: state the ceiling honestly (already in repo data).

## Engineer B — "the empiricist"
Problems found:
4. **Unverifiable grounding.** Claims like "REx lifts every model to 0.86" are repo-internal; if the
   doc cites a number it must be attributable, not floated. → Fix: cite numbers as *this repo's
   measured result* with the file (`ARCHITECTURE.md` / `rex/frontier.py`), not as universal truth.
5. **Sample-efficiency cell risks false precision.** Saying "RLHF needs ~50k comparisons" invents a
   number. → Fix: say "tens of thousands of human comparisons (order-of-magnitude, varies by setup)"
   — qualitative, not a fake figure.
6. **Validator doesn't test failure.** A validator that only passes proves little. → Fix: the script
   self-tests by mutating a copy of the matrix (blank a cell, bad path) and asserting it *rejects* —
   so we demonstrate it actually catches violations.

## Engineer C — "the scope skeptic"
Problems found:
7. **Category-error not fully neutralized.** Even with a domain column, a reader may still read the
   table as "code-as-policy wins 4/5 axes." → Fix: add an explicit caveat row/sentence that the
   axes are not a scorecard; each paradigm is best *in its domain*.
8. **Interpretability nuance.** RLHF/CAI aren't *zero* interpretability — the constitution itself is
   human-readable text (CAI's selling point!), and reward models can be probed. → Fix: don't paint
   weight-based methods as fully opaque; CAI's constitution is in fact MORE legible than a code
   reward in plain English, even if its *effect* on weights is opaque. Nuance both directions.
9. **Over-engineering check.** Three artifacts is the right amount; do NOT add a plotting script or
   a second matrix format — that's gold-plating for a theory task. → Kept minimal.

## Final filtered spec (deltas applied)
- comparison.md: describe CAI's **two stages**; include RLHF **KL-to-reference**; state the
  **frozen-model ceiling**; attribute repo numbers to repo files; keep efficiency **qualitative**;
  add **"not a scorecard"** caveat; give CAI credit for a **human-readable constitution** (nuanced
  interpretability, both directions).
- validate_matrix.py: add **negative self-tests** (blanked cell + bad path must be rejected).
- Scope held to exactly 3 artifacts.
