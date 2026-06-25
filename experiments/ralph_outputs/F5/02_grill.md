# F5 — Grill: 5 personas × 3 rounds on the abstract

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**,
**AAAI Reviewer (REV)**, **RL Engineer (RLE)**, **DevOps Lead (DVO)**.

## Round 1 — initial take

**SMR.** The three-claim decomposition (harness / transfer / training-signal) is the
spine and it's good — separable, measurable. But the draft abstract says "large,
statistically significant pass@1 lift on cascades." Is that *measured* or *planned*?
The McNemar test in §5.2 is on a 30×5 grid the outline marks partly pending. An abstract
that asserts significance the results section hasn't locked is a desk-reject risk.

**PSRE.** I love the trap-action framing — that's the real-world pain. The CoreDNS /
InnoDB / NLB examples are exactly the cascades that page me at 3am. The abstract should
keep "the naive fix worsens the outage." That's the sentence an SRE remembers. Don't cut
it for word count.

**REV.** Word count: AAAI doesn't hard-cap abstracts but ~150–250 is the norm; the draft
is ~230, fine. My problem is *credibility of numbers*. "89.7% held-out verifier accuracy,
approaching 94.9% hand-written" — three held-out incidents (`harness_synth.json`) is a
tiny n. Citing two decimals on n=3 looks like false precision. I'd round and soften.

**RLE.** The abstract sells "REx with SME feedback yields a large lift… collapses without
SME feedback." But `headline_insights.md` §3 says the collapse *is the finding*: with the
hint stripped REx → 0.25 ≈ zero-shot 0.24. That's an honest negative, and it's the most
defensible thing here. The abstract currently buries it as a caveat. Lead with the
verifiable env + searched verifier as the contribution; treat the loop honestly.

**DVO.** "Deterministic verifiable reward, no LLM judge" is the operationally important
bit — reproducible, credit-free, runs offline. The note that the Anthropic account was
out of credits but evals were unaffected is a *feature* of the design. Worth one clause.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**RLE → REV.** I disagree with REV's "just round the numbers." Rounding 89.7→90 doesn't
fix the n=3 problem; it hides it. The honest move is to cite the insight-doc framing:
"0.90 vs 0.95 hand-written on held-out hazards, compressing 14→3 rules with zero
synthesis-quality misses." That's defensible *because* it states the one miss is an
unseen hazard. Precision isn't the sin; unsupported precision is.

**REV → RLE.** Pushing back. You want to put the *negative* (oracle leakage) in the
abstract's spotlight. That's intellectually honest but strategically it reads as "our
main method doesn't work." An AAAI abstract has ~10 seconds to earn a "maybe accept." I'd
state the limitation in ONE clause, not lead with it. Lead with what *does* hold: the
synthesized verifier generalizes, and the reward is deterministic. Honesty in the body,
hook in the abstract.

**SMR → REV.** I side with RLE over you here. The field is drowning in abstracts that
hook with a lift and bury the ablation. The reason this paper is interesting is *exactly*
that the honest ablation relocated the contribution from "clever loop" to "verifiable
env + learned verifier." If we hide that, a reviewer who reads §6 feels misled and gets
angrier than one who saw it coming. State it plainly, briefly.

**PSRE → DVO.** DVO wants a clause on credits/offline. Agree it matters, but for an
*SRE* audience the killer is not "credit-free," it's "the verifier is ground truth: a
simulator checks whether the SLO actually recovered." Spend the scarce words there, not
on billing.

**DVO → SMR.** Fine, but don't let SMR's "lead with the negative" turn the abstract into
a mea culpa. The transfer claim (C2 / FIREBALL) is genuinely novel and is marked
*pending* in the outline. Don't assert C2 as a result. Either omit it or frame it as a
hypothesis. Asserting an unrun result is worse than any honesty problem.

## Round 3 — synthesis

Consensus the abstract must:
1. **Keep the trap-action hook** (PSRE) — cascades where the naive fix worsens the outage.
2. **Decompose into the three components** (SMR) but only *assert* what's measured.
3. **Report verifier generalization honestly**: ~0.90 vs ~0.95 hand-written, 14→3 rules,
   one miss = an unseen hazard (RLE). No false precision.
4. **State the oracle-leakage / SME-dependence finding plainly but in one clause**, not
   as the lead (REV vs SMR compromise): the lift *depends on* SME feedback; stripped of
   it, REx ≈ zero-shot — an honest generalization boundary.
5. **Do NOT assert C2 transfer as a result** (DVO) — frame as ongoing / omit; the outline
   marks it pending.
6. **Emphasize the deterministic verifiable reward** as the reproducibility contribution
   (DVO), but ground it in "simulator = ground truth" (PSRE), one clause on credit-free.
7. **Name released artifacts** (harness, simulator, benchmark, deterministic reward).
8. **Hard word gate ≤250**, counted.

Open disagreement left unresolved (documented, not papered over): REV still thinks the
honest negative costs us at the abstract stage; SMR/RLE think it earns credibility. I
take SMR/RLE's side but honor REV by keeping the negative to a single, non-dwelling clause.
