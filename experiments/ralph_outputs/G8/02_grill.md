# 02 — Grill (5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (AAAI)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial takes

**SMR:** The differentiator that will survive scrutiny is the *verifiable, root-cause-aware
reward* and the *learned verifier* (Thompson-tree over rules-as-data, 14→3 rules, 0.90 held-out
accuracy). That is a real research contribution. Lead with it. The REx lift is softer — the
ablation already shows most of it was oracle leakage. Do not let the one-pager pretend REx is the moat.

**PSRE:** What I care about: does this map to real outages? 19 reconstructed post-mortems
(AWS DynamoDB DNS, Cloudflare WAF, GitHub MySQL, Slack Consul) is the credibility hook for any
SRE buyer. The "loudest alert points at a victim, not the cause" framing is exactly the on-call
pain. Trap-action grading (penalize the fix that *worsens* the incident) is the safety story
that no eval harness I've seen has.

**AAAI:** A "benchmark" claim needs (a) public substrate not contaminated, (b) within-group
reward spread, (c) a held-out generalization result. We have (b) (0.0/0.15/1.0 spread) and (c)
(the verifier generalizes to 3 unseen incidents). (a) is the risk — these are *public*
post-mortems, so frontier models may have read them. The one-pager must not claim "uncontaminated."

**RLE:** The deployable asset is the *environment + grader*, model-frozen. "Small + REx beats
big zero-shot" (haiku+REx 0.86 > opus zero-shot 0.81) is a great line — but it's on the easy
tier and partly leakage. The harder-tier curriculum (zero-shot floors at 0.19–0.42, REx ~triples
but mostly via *escalation*, not faked fixes) is the more honest and more interesting story.

**DOL:** For partners, the wedge is "open graduation benchmark." That phrase only lands if it's
actually *open* — runnable with one command, swappable models, no vendor lock. We have that
(`python3 -m rex.frontier`, HUD gateway = 200+ models behind one key). Sell the openness.

## Round 2 — react to another persona by name (forced disagreement)

**RLE → SMR:** I disagree with burying REx. You're so worried about the ablation that you'd
gut the most legible demo we have. The ablation says REx's lift *on the easy tier with oracle
hints stripped* collapses — fine. But the **safety-gate behavior** (every model converges to
0.86 = solve 4, *escalate* the 1 unsolvable instead of flailing) is REx doing real work that
best-of-N does NOT replicate. Don't throw the loop out; reframe what it buys.

**SMR → RLE:** Partially fair, but you're moving the goalposts. The 0.86 convergence is on the
*easy* set where the ceiling is structural, not earned. If the one-pager leads with REx and a
reviewer runs the ablation, we lose all credibility. My position stands: *environment + verifier
are the moat; REx is a feature, with the escalation behavior as its honest selling point.*

**AAAI → DOL:** Your "open benchmark" framing is the most dangerous line in the doc. "Open" +
"benchmark" invites the contamination question immediately. These are public post-mortems; a
model trained post-2025 has likely seen the AWS DynamoDB write-up. If we say "graduation
benchmark" we are inviting "you're testing memorization." You must qualify it.

**DOL → AAAI:** You're over-indexing on the academic frame. Investors aren't AAAI reviewers.
"Open" to a partner means *runnable, swappable, no lock-in* — that's a moat against closed eval
vendors, not a contamination claim. But I concede the wording: I'll say "open graduation
benchmark **(reconstructed real cascades, grading the mechanism not the text)**" so the
contamination defense is baked into the phrase.

**PSRE → SMR:** I'll push back on you too. You keep calling the verifier "the research
contribution" as if SREs care. They don't. The buyable thing is *the trap penalty stopping the
agent from scaling a crash-looping control plane and herding its datastore.* Lead the SRE-facing
line with the *failure it prevents*, not the Thompson tree. Mechanism = engineer appendix.

## Round 3 — synthesis

Consensus the personas converge on:
1. **Moat = the verifiable environment + the trap-aware/learned verifier.** Not the refinement
   loop. (SMR wins the framing; RLE wins a carve-out.)
2. **REx stays, reframed as the safety/escalation behavior**, not as a raw-lift headline.
   "Converges to 0.86 by *escalating* the unsolvable incident" is the honest, distinctive line.
3. **"Open graduation benchmark" must be qualified in-phrase** — grade the *mechanism*, on
   *reconstructed real cascades*, model-frozen and one-command-runnable. Never claim
   "uncontaminated." (DOL + AAAI compromise.)
4. **SRE-facing copy leads with the prevented failure** (trap), engineer copy carries the
   mechanism. (PSRE.)
5. **Include the honest ablation caveat on the page.** Honesty is itself a differentiator vs
   demo-ware competitors. (SMR/AAAI, unanimous.)
