# F3 — Improved Plan (post-grill)

## What changed vs `01_plan.md`

### Accepted critiques
1. **(DOL) Disarm the CI/CD reading in the first paragraph.** Add an explicit
   definition: *deployment* = the stance "passed an eval once → trusted by default";
   *graduation* = "trust earned per tier and revocable." Without this, half of an ops
   audience reads the title as "we didn't ship."
2. **(AAAI/RLE) Lead evidence with behavior, not the reward formula.** The strongest proof
   the "exam can't be crammed" is the *empirical escalation signature*: with REx every model
   converges to 0.86 = solve-4 + correctly-escalate-1, and hard-tier zero-shot floors at 0.0
   on several incidents. Formula supports the behavior; behavior leads.
3. **(RLE) Add the curriculum result as the headline graduation fact.** "small + REx beats
   big zero-shot" (haiku+REx 0.68 > opus zero-shot 0.42; full-tier haiku+REx 0.86 > opus
   zero-shot 0.81). The *program* confers competence the raw model lacked — pure graduation.
4. **(AAAI) Argue, don't assert, the 0.86 ceiling.** Show `(4×1.0 + 0.30)/5`.
5. **(SMR/PSRE) State the honest limit explicitly.** Add a "what this degree does NOT
   certify" subsection: demotion/revocation is *designed and partially exercised, not fully
   automated*; n is small (5 incidents × 5 models, plus the 15+5 curriculum); the diagnosis
   judge is an LLM. No silent gaps.
6. **(PSRE) Make the credential tiered + revocable + scoped, never blanket prod autonomy.**
   Tie directly to `autonomous/approval/blocked`.
7. **(DOL) Keep the compression result prominent** (baselines 0.63–0.81 → uniform 0.86):
   institutional accreditation standardizes heterogeneous models to one bar.

### Rejected critiques (with reasons)
- **(SMR, R1) "If revocation isn't automated in code today, cut the metaphor."** Rejected,
  per PSRE's R2 rebuttal that SMR conceded. The promotion/demotion arrow is *designed*
  (README:77-79) and the gating direction is *exercised* by the safety gate that escalates
  rather than acting unsafely. A designed-and-partially-exercised mechanism honestly supports
  the frame **provided** the limitation is stated aloud (which we now do, accepting #5). Cutting
  a correct, well-grounded metaphor over a future-work gap would be an overcorrection.
- **(AAAI, implicit) "n=5 is too small to conclude anything."** Partially rejected: we do not
  drop the conclusions, but we *scope* them — the claim is about *within-group signal and the
  direction/shape of the effect* (escalation behavior, spread compression), which are visible
  even at n=5, not about a population-level effect size. Caveat stated, claim scoped.

## Final structure of `CONCLUSION.md`
1. **Stance: graduation, not deployment** (define both terms; kill the CI/CD reading).
2. **What makes graduation real** — 4 mechanisms, each → a file.
3. **Evidence** — behavior first (escalation, small+REx>big-zero-shot, 0.86 ceiling argued,
   spread compression), reward math in support.
4. **What this degree certifies — and what it does not.**
5. **Future cohorts** (automate demotion; widen the curriculum; independent oracle).
6. **Closing line.**

## Unchanged
Artifacts list, no-core-edit rule, validator approach.
