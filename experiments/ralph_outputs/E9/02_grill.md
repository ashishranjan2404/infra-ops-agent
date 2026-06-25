# E9 — 02 Grill (Ralph Loop, 5 personas, 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **AAAI** (AAAI Reviewer),
**RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial take

**SMR:** The honest framing is data quality, not a trained run. "Which helps more" for
seeding a policy reduces to coverage × within-group spread × domain match. Transfer from
FIREBALL is the *negative-control* arm: D&D combat state is structurally similar but
semantically off-domain. I expect synthetic-in-domain to win on every axis that matters.

**PSRE:** I care about whether the synthetic trajectories are *plausible incidents*. If the
augmenter just shuffles tool names, an SRE will see through it instantly. The positive
trajectory must end on the canonical fix and the negatives must include the real trap
actions from each scenario, or it's not teaching anything.

**AAAI:** A comparison where one arm is "blocked" and the other "runs" is not a comparison —
it's one measured arm and one excuse. To be publishable you must score BOTH arms on the
SAME metric vector, even if the Fireball arm scores zero on domain match. Otherwise reject.

**RLE:** Within-group reward spread is the whole game for RFT/GRPO. A group of all-1.0 or
all-0.0 trajectories has zero gradient. The augmenter MUST emit a positive AND a graded set
of negatives per scenario or the data is untrainable regardless of which arm produced it.

**DOL:** Reproducibility. If I rerun the augmenter I must get byte-identical output, or the
"comparison" drifts between runs. Seed everything. No wall-clock, no unseeded RNG, no LLM.

## Round 2 — react to another persona by name (genuine disagreement)

**RLE → AAAI:** I disagree with "score both on the same vector or reject." Forcing a fake
symmetric number onto the Fireball arm (e.g. pretending it has a within-group SRE reward)
would be *fabrication* — the brief explicitly forbids faked results. The honest move is:
score both on the metrics that are *definable a-priori* (domain_match, coverage, n) and mark
spread `null` for Fireball because no SRE reward exists over D&D state. That's rigorous, not
an excuse.

**AAAI → RLE:** Fair, but then your verdict must NOT say "synthetic wins on spread" as if it
beat a real number — it beat `null`. State that the spread comparison is vacuous on the
Fireball side. I'll accept `null` if the caveat is explicit.

**PSRE → SMR:** I push back on "synthetic-in-domain wins on every axis." It does NOT win on
*diversity of reasoning*. Every synthetic positive walks the same canonical path; a frozen
LLM trained on that will overfit to one investigation shape. FIREBALL, off-domain as it is,
at least contains *human* improvisation. So "helps more" depends on whether you want
coverage (synthetic) or reasoning diversity (transfer). Don't oversell.

**DOL → SMR:** Agree with PSRE — and operationally, synthetic data that's too clean teaches
the model to expect clean signals. Real incidents are noisy. The augmenter should at least
*perturb* surface form (paraphrase, tool-order shuffle, jitter) so it's not 51 photocopies.

**SMR → PSRE:** Conceded on reasoning diversity — that's a real limitation of the synthetic
arm and I'll put it in the critique. But for *seeding* (cold-start SFT before any RFT),
coverage and label-correctness dominate; diversity is a second-stage concern. So the verdict
stands for the seeding question, with diversity flagged as the synthetic arm's known weakness.

## Round 3 — synthesis

Consensus reached:
1. **Score both arms on a shared metric vector**, but use `null` (not a faked number) where
   a metric is undefinable for an arm (Fireball spread). Caveat must be explicit (AAAI/RLE).
2. **Positives must end on the canonical fix; negatives must include real trap actions** and
   be graded so within-group spread > 0 (PSRE/RLE).
3. **Perturb surface form** (paraphrase + tool-order + jitter), seeded for reproducibility
   (DOL).
4. **Verdict is a data-quality / seeding verdict, not a trained-accuracy verdict**, and must
   name the synthetic arm's weakness: low reasoning diversity (SMR/PSRE).
5. The Fireball blocker is real and threefold (no vendored dataset, frozen-LLM project has no
   fine-tuning stack, off-domain) — document, don't fake.
