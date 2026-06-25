# J10 — Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (AR)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR.** A "lessons from production" section with no production is a credibility minefield.
The only defensible version anchors every transferable lesson to an artifact we actually
produced. The strongest real lesson is D13: the reward is gameable, so any policy we ship
is optimizing a *proxy*. That's a genuine ML insight, not hand-waving.

**PSRE.** I don't care about your reward math. I care: will this thing `restart_service` on
a crash-looping control plane at 3am and herd the datastore? The trap-action list in
`scoring.py` is author-enumerated. In prod the action space is open. So the honest headline
is: **we have no evidence trap-safety generalizes off-distribution.** Say that loudly.

**AR.** Reviewer reflex: "lessons from production" in a paper with zero production runs is a
rejection trigger unless reframed. Retitle the contribution as *deployment-readiness
analysis*, not deployment results. Then the absence of prod data is a scoped limitation,
not a lie. I'll reject if I see a single unsourced MTTR percentage.

**RLE.** Distribution shift is the whole game. We trained/eval'd on 61 CIDG scenarios (A16),
4 of which have wrong-target fixes and 3 of which throw KeyErrors on metrics the engine
doesn't even model. So the policy learned on a substrate with known holes. Lesson: the
eval ceiling is bounded by substrate fidelity. That belongs in the section.

**DOL.** Operationally the only safe first step is **shadow mode**: agent proposes, human
executes, we diff. We have not run shadow mode. So we can describe the *protocol* but must
state we have zero shadow-mode data. Also: rollback. Nobody mentioned rollback. A prod
remediator needs a documented blast-radius/rollback story before it touches anything.

## Round 2 — react to another persona BY NAME (force disagreement)

**PSRE → SMR.** I disagree with SMR's framing that D13 is "the strongest lesson." D13 is a
reward-hacking result against a *judge*, not against a cluster. For an SRE audience the
reward hack is secondary; the primary risk is the *action layer*. A model can have a
perfectly honest diagnosis and still execute a catastrophic fix. Lead with action safety,
not reward integrity.

**SMR → PSRE.** Partially wrong. Reward integrity and action safety aren't separable: the
policy *learns its action distribution from the reward*. D13 shows a hedge diagnosis +
legitimate fix scores 0.55 — i.e. the optimizer is rewarded for non-committal behavior.
A non-committal agent in prod is exactly the agent that takes a "safe-looking" but useless
action. So reward hacking *is* an action-safety story. But I concede the section must SURFACE
the action-layer consequence explicitly, not bury it in reward math.

**AR → DOL.** I push back on DOL treating shadow mode as a checkbox. If we write a shadow-mode
"protocol" with no data, a reviewer will ask: what's your acceptance threshold? "Agent
proposes, human executes" is not a result; it's a plan. Either give a *measurable* shadow
criterion (e.g. action-agreement rate vs. on-call, trap-proposal rate ≤ X over N incidents)
or don't dignify it as a lesson — file it as future work.

**DOL → AR.** Fair, and I'll go further than you want: I'll define the acceptance gate
numerically *as a target to be validated*, clearly labeled "not yet measured." That's not
fabrication — it's specifying the experiment. A readiness section that can't state its own
pass/fail gate is useless to whoever actually has to sign the deploy ticket.

**RLE → SMR.** I disagree that substrate holes are just a footnote. A16's 7 broken scenarios
mean some fraction of training reward was *unattainable or mis-specified*. If the engine
KeyErrors on `latency_p99_ms`, the policy never learned that SLO dimension at all. Under
distribution shift to a real cluster that DOES track p99, the agent is blind on an axis it
was never trained on. That's a first-order deployment risk, not a footnote.

**PSRE → RLE.** Agreed and that's scarier than D13. But note the flip side: the sim's
*conservatism* may be protective. The engine not modeling hysteresis means we never trained
the agent to exploit reset-by timing — so we also didn't train risky "wait it out" behavior.
Don't only frame substrate gaps as bad; frame them as *unknown-direction* bias.

## Round 3 — synthesis

Convergence:
1. **Reframe the title's promise.** This is a *deployment-readiness analysis*, not deployment
   results (AR). No production experience will be fabricated.
2. **Lead with action-layer safety, then reward integrity as its driver** (PSRE + SMR
   reconciliation). D13's hedge→0.55 result is presented as an action-safety consequence.
3. **Substrate fidelity bounds everything** (RLE + PSRE): cite A16's 7 broken scenarios and
   the unmodeled metrics; frame engine gaps as *unknown-direction* bias, not purely negative.
4. **Every gap gets a measurable acceptance gate, explicitly labeled "target, not measured"**
   (DOL + AR). Shadow-mode action-agreement & trap-proposal rate; distribution-shift trap
   recall; MTTR measurement plan tied to A9's incomplete labels.
5. **Add rollback / blast-radius** to the readiness checklist (DOL) — it was missing.
6. **MTTR honesty** (AR + A9): 12/30 real incidents have unknown MTTR, so we cannot and will
   not state an MTTR delta; we state the measurement protocol instead.

Rejected: PSRE's "reward hacking is secondary, drop it" — rejected because SMR showed reward
shape drives the action distribution; we keep D13 but recast it as action-safety-relevant.
