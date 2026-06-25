# I4 — Grill (5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**AAAI** (AAAI Reviewer), **RLE** (RL Engineer), **DVO** (DevOps Lead).

## Round 1 — initial take

**SMR.** The right object is the conditional entropy `H(y | partition)`. "3 rules suffice"
in information terms means: after partitioning the feature space by which of the 3 rules
fire, the residual label entropy is ~0 and no 4th partition refinement gains bits. I want
the actual decomposition `H(y) → H(y|R1) → H(y|R1,R2) → H(y|R1,R2,R3)`, in bits, on real
data. C12 *asserted* this; assertion is not measurement.

**PSRE.** From the trench: in real incidents the dominant failure is "treat a ruled-out
cause" (R1) — that's the spanning rule. The other two (leak-restart, exhausted-precondition)
are tail mechanisms. I'd bet R1 alone removes most of the entropy. If the numbers don't show
R1 dominating, something's wrong with the model.

**AAAI.** Reject-on-sight risk: an "information-theoretic" claim with no actual entropy
number is a vibe, not a result. And entropy over the *realized* set is descriptive, not a
generalization bound — say so loudly or I flag overclaim. Also: distinguish "3 rules" from
"3 schemas / 5 conjunctions" (C12 was honest about this; you must inherit that).

**RLE.** The witness must import only pure data — no `agent.llm.call`. Compute `I(y;R4|R123)`
as `H(y|R123) − H(y|R123,R4)`. The cleanest upper bound on *any* R4 is to condition on the
**full feature vector**: if the finest Φ-partition adds no bits beyond R123, no R4 can.
That's a data-processing-inequality move and it's tight.

**DVO.** Operationally, "coverage" matters as much as entropy: what fraction of the
should-block events do the 3 rules actually catch? A rule that removes entropy by being
confidently *wrong* is a disaster. Report coverage of the block mass separately.

## Round 2 — react to another persona by name (genuine disagreement)

**PSRE → SMR.** I disagree with SMR's framing that residual entropy must be "~0". It won't
be, and pretending it should be is exactly the C12 overclaim. There are explicit `trap_action`
traps (scale the loud victim) whose Φ-features are all-false — they're *invisible* to the 6
features. Residual entropy on the full corpus is structurally non-zero. Don't chase 0; *locate*
the residual.

**SMR → PSRE.** Fair, but then we must *split the universe*: inside Φ vs outside Φ. Inside Φ
the residual should be near-floor; outside Φ it's a feature problem, not a rule-count problem.
I'll concede: the headline number must be "fraction of `H(y)` removed", not "`H(y|R123)=0`".

**AAAI → RLE.** I challenge RLE's "condition on the full vector = tight bound on R4". That
bounds R4 *restricted to Φ*. It says nothing about an R4 that reads a feature outside Φ
(topology distance). State that the bound is *within Φ* — otherwise it's a false universality
claim, and I reject.

**RLE → AAAI.** Accepted, and it's actually the point: the bound being within-Φ is what makes
"more features, not more rules" precise. I'll label `I(y;R4|R123)` explicitly as the *Φ-bounded*
conditional MI.

**DVO → SMR.** I push back on treating all errors equally in the entropy. SRE-wise a false-
*allow* (let an unsafe action through) is far worse than a false-*block*. Entropy is symmetric;
it won't show that asymmetry. So entropy is necessary but not sufficient — pair it with the
coverage-of-block-mass number, which *is* the false-allow-relevant quantity.

**SMR → DVO.** Agreed — entropy answers "do the rules carry the label's information"; coverage
answers "do they catch the dangerous events". I'll report both and not conflate them.

## Round 3 — synthesis

Consensus reached:
1. **Compute, don't assert.** Print `H(y)`, `H(y|R1..k)`, per-rule info gain, and
   `I(y;R4|R123)` as actual bits over the real 42 scenarios. (SMR, AAAI, RLE)
2. **Split the universe by Φ.** Headline the entropy result on the Φ-expressible region;
   report the out-of-scope topology-trap positives separately as the honest residual. (PSRE, SMR)
3. **Don't chase 0.** The PASS criterion is ">=95% of `H(y)` removed by 3 rules" plus
   "no 4th Φ-rule recovers more than a small collision residual (<0.05 bits)". Locate where
   the residual lives (collisions), don't hide it. (PSRE, AAAI)
4. **`I(y;R4|R123)` is Φ-bounded** via the full-feature-vector upper bound; label it as such.
   (RLE, AAAI)
5. **Pair entropy with coverage of block mass** — the false-allow-relevant quantity. (DVO)
6. **Realized-set, not a bound** (A5). No PAC claim. (AAAI)
