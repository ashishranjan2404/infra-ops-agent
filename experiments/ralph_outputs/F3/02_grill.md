# F3 — Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **AAAI** (AAAI Reviewer),
**RLE** (RL Engineer), **DOL** (DevOps Lead). Topic: the Conclusion's "graduation not
deployment" framing.

## Round 1 — initial takes

**SMR.** I like the frame because it resists the field's worst habit: treating an eval pass
as a license. "Graduation not deployment" is really "continuous tiered evaluation, not a
one-shot gate." But a Conclusion is where reviewers hunt for overclaim. The metaphor must be
*falsifiable* — tied to a mechanism that could in principle revoke the credential. If it's
just a nice sentence, cut it.

**PSRE.** From an on-call seat, the metaphor is dangerously close to a lie if "graduate"
implies "now run unattended in prod." Real SRE autonomy is *scoped and revocable*: you get the
pager for one service, supervised, and you lose it after one bad page. So the Conclusion is
only honest if it says graduation confers **tiered, revocable** trust — exactly the
`autonomous/approval/blocked` tiers in `tools_registry.json` — and not a blanket prod license.

**AAAI.** Conclusions don't get a pass on rigor. Three things will draw fire: (1) Is the
0.86 ceiling *argued* or *asserted*? You must show it's `(4×1.0 + 0.30)/5`, i.e. solve-4 +
escalate-1, not saturation. (2) n is tiny — 5 incidents, 5 models. Say so. (3) The judge is an
LLM; "mechanism-aware exam" is a strong claim that needs the anti-gaming reward math in view.

**RLE.** My worry is the reward, since the whole "can't cram the exam" line rides on it. State
it exactly: `0.30·diagnosis + 0.25·fix + 0.45·resolved − 0.60·trap`. The key fact that sells
the metaphor is that `resolved` alone caps at 0.45 — you cannot deploy/restart your way to a
degree. If the Conclusion hand-waves the reward, the metaphor is unearned.

**DOL.** Operationally, "deployment" is a loaded word for my audience — it means CI/CD push.
Be careful the title doesn't read as "we didn't ship." Make explicit that *deployment*
here = the cultural stance "passed once, trusted thereafter," and *graduation* = "trust is
earned per-tier and can be pulled." Otherwise half the readers think it's about Kubernetes.

## Round 2 — react to another persona (genuine disagreement)

**PSRE → SMR.** I disagree that the credential must be *revocable in code today* to be
honest. SMR wants a live demotion mechanism or "cut the metaphor." That's too strict for a
Conclusion. The repo *designs* promotion/demotion (README:77-79) and *demonstrates* the
gating direction (the safety gate that escalates). It's honest to say the demotion arrow is
**designed and partly exercised, not yet automated** — and call that a limitation. Demanding
full RLHF-driven revocation before you may use the word "graduation" throws out a correct,
well-grounded frame.

**SMR → PSRE.** Fair, but then the Conclusion must *say that sentence out loud* — "demotion
is designed, not automated" — in the limits paragraph, or AAAI eats us. I'll concede the
metaphor can stand on a designed-and-partially-exercised mechanism, *if and only if* the honesty
is explicit. No silent gaps.

**AAAI → RLE.** RLE says quoting the reward formula sells the metaphor. I push back: the
formula alone is not evidence the exam is *uncrammable* — a reward-hacker could still maximize
`diagnosis` via judge sycophancy. The Conclusion's claim is only safe because of the *empirical*
result: with REx every model converges to **0.86 = solve-4 + escalate-1**, and the hard-tier
zero-shot models *floor at 0.0 on several incidents*. That behavioral signature — escalating the
unsolvable one instead of faking a fix — is the real evidence, not the formula. Lead with the
behavior.

**RLE → AAAI.** Agreed and I'll go further: cite the curriculum result too — hard-tier
zero-shot 0.19–0.42, REx ~triples it to 0.59–0.71, and **haiku+REx (0.68) > opus zero-shot
(0.42)**. That "small + REx beats big zero-shot" is the single most graduation-shaped fact: the
*program* (curriculum + refinement + gate) confers competence the raw model didn't have. The
degree is conferred by the institution, not innate.

**DOL → AAAI.** I think AAAI is underweighting the operational payoff in the rush for rigor.
The compression result — baselines 0.63–0.81 collapsing to a uniform 0.86 with REx — is what an
ops org cares about: it means the *process* standardizes wildly different models to one bar.
That's the institutional accreditation story. Don't bury it as a footnote to the n=5 caveat.

## Round 3 — synthesis

Consensus the Conclusion must hit:
1. **Define terms up front** (DOL): deployment = "passed once → trusted by default";
   graduation = "trust earned per tier, revocable." Disarm the CI/CD reading immediately.
2. **Ground in 4 named mechanisms** (all): trust tiers (`tools_registry.json`), the
   uncrammable reward (`rex/scoring.py` math), the curriculum-as-degree-program
   (`rex/curriculum.py`), and escalation-as-passing (the 0.86 ceiling argument).
3. **Lead the evidence with behavior, not formula** (AAAI/RLE): escalating the unsolvable
   incident; small+REx beating big zero-shot; the spread compressing to 0.86.
4. **Argue the ceiling** (AAAI): 0.86 = `(4×1.0+0.30)/5`, not saturation.
5. **State the honest limit out loud** (SMR/PSRE): demotion/revocation is *designed and
   partially exercised, not fully automated*; n is small (5 incidents × 5 models); judge is an
   LLM. A "what this degree does NOT certify" subsection.
6. **Tiered + revocable, not blanket prod autonomy** (PSRE): the credential is scoped.
