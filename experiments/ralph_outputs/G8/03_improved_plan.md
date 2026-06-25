# 03 — Improved Plan

## What changed after the grill

**Accepted:**
- **Lead with the verifiable environment + trap-aware/learned verifier as the moat** (SMR, PSRE,
  AAAI). REx is demoted from "headline lift" to "the safety/escalation behavior." This reorders
  the whole one-pager: Wedge → Moat → Proof → Honest caveat → Ask.
- **Qualify "open graduation benchmark" in the phrase itself** (DOL + AAAI compromise): "grading
  the *mechanism* on *reconstructed real cascades*, model-frozen, one command." Never claim
  "uncontaminated." Add an explicit "what we do NOT claim" line.
- **SRE-facing copy leads with the prevented failure** (PSRE): the trap penalty stops the agent
  scaling a crash-looping control plane and herding its datastore. Mechanism (Thompson tree,
  14→3 rules) goes in a one-line "for engineers" aside, not the headline.
- **Put the honest ablation caveat ON the page** (unanimous): state plainly that REx's raw lift
  was largely oracle-feedback leakage and that the defensible contributions are the environment
  and the searched verifier. Honesty as a differentiator.
- **Use the harder-tier curriculum as the more honest proof** (RLE): zero-shot floors 0.19–0.42,
  REx ~triples it and *escalates* the unsolvable cases rather than faking fixes.

**Rejected (with reasons):**
- **RLE's push to keep REx as a headline raw-lift number** — rejected. A reviewer who runs the
  ablation would torch a REx-led pitch. We keep REx, but framed as escalation/safety behavior,
  which is what survives the ablation. (SMR's rebuttal held.)
- **DOL's unqualified "open benchmark" hook** — rejected as written; accepted only with the
  in-phrase contamination defense. The bare phrase invites the memorization attack.
- **PSRE's "SREs don't care about the verifier"** — partially rejected. SREs don't care about
  the *Thompson tree mechanism*, agreed, but they do care that the safety harness *generalizes
  to unseen incidents* (0.90 held-out). We keep the generalization claim, drop the mechanism
  jargon from the headline.

## Final structure of the one-pager
1. **One-line thesis** (the cascade misleads frontier models; grade root-cause+fix+trap, not "did it come back up").
2. **The wedge** — open graduation benchmark (qualified) + trap-action safety.
3. **The moat** — verifiable environment, learned/generalizing verifier, two-tier fidelity (sim + live GKE), model-frozen.
4. **Proof points** — 3-4 cited numbers from real runs.
5. **What we do NOT claim** (the honesty block).
6. **The ask** (partners / investors).

Plus `artifacts/proof_points.json` so every number is auditable.
