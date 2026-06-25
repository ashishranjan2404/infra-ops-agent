# 02 — Grill (5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (REV)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial takes

**SMR:** A "code-as-policy vs RLHF vs CAI" comparison is only rigorous if it separates *what is
being optimized*. RLHF optimizes **weights** against a learned reward model; CAI also optimizes
weights but swaps the human label for an AI label conditioned on a constitution. Code-as-policy
here optimizes **code**, not weights. If the doc blurs that, it's pop-sci. The axis "where
knowledge lives" is the load-bearing one — get it exactly right.

**PSRE:** From an operations seat, the only axis I trust is **verifiability**. In this repo a fix
is "correct" iff the SLO metric crosses back AND the trap wasn't tripped (`rex/scoring.py`). That's
a *ground-truth* signal. RLHF/CAI rewards are *learned approximations* of human taste — there is no
oracle. The doc should hammer that asymmetry and not let RLHF off the hook on reward hacking.

**REV:** I will reject this if it reads as advocacy. Code-as-policy is *not* a general alignment
method — it works only where you can write a verifier. RLHF/CAI target open-ended helpfulness/
harmlessness where no verifier exists. Comparing them head-to-head on one table risks a
category error. The paper must scope each paradigm's *domain of applicability*.

**RLE:** Mechanically: RLHF = reward model + PPO + KL-to-reference. CAI = (1) supervised stage of
self-critique-and-revise, then (2) RLAIF where the preference model is trained on *AI* comparisons
guided by constitution principles. Code-as-policy here isn't doing policy-gradient at all — it's
**search** (Thompson sampling over refinement candidates, `rex/tree.py`) plus a **rejection gate**.
Calling it "RL" loosely would be wrong; it's closer to inference-time search + verification.

**DOL:** I care about **sample efficiency** and cost. RLHF needs tens of thousands of human
comparisons + a training run. CAI removes most human labels but still trains. Code-as-policy needs
**zero** preference labels and zero training — but pays at *inference* time (multiple model calls
per incident in the REx loop). The doc must say efficiency is measured in different currencies:
human-labels + GPU-hours vs inference-calls. Don't compare apples to GPU-hours.

## Round 2 — react to another persona BY NAME (forced disagreement)

**REV → PSRE:** I disagree with PSRE's "verifiability is the only axis I trust." That's exactly the
bias that makes this comparison unfair. Most of what RLHF/CAI are *for* — tone, refusal calibration,
harmlessness, honesty — is **inherently unverifiable**; there is no SLO for "was this answer
condescending." Privileging verifiability stacks the deck for the home team. The doc must concede
that code-as-policy's verifiability is a property of the *task* (incident response has an oracle),
not a property of the *method* that transfers to alignment writ large.

**PSRE → RLE:** Pushing back on RLE's "calling it RL would be wrong." Operationally I don't care if
it's policy-gradient or search — the *system* is a closed loop that improves a measured outcome, so
practitioners will call it RL-ish whether you like it or not. But fine, for a rigorous doc, concede
the point and label it precisely: **verifier-guided inference-time search over a frozen policy**.

**SMR → DOL:** I disagree with DOL's framing that efficiency is "different currencies, don't
compare." You *can* compare — on **marginal cost to improve behavior on a new task**. RLHF/CAI
amortize a big upfront training cost across all future queries (cheap at inference). Code-as-policy
has near-zero upfront cost but **re-pays search cost on every incident**. That's a real, comparable
tradeoff: amortized capex vs per-call opex. The doc should state it as that, not punt.

**RLE → REV:** I partly disagree with REV's "category error / don't put them in one table." The
unifying frame *does* exist: all three are ways to inject **human normative knowledge** into model
behavior — RLHF via labels→reward-model→weights, CAI via constitution→AI-labels→weights,
code-as-policy via **explicit code** (the reward function, the safety gate, the registry). Same
goal, different substrate for the knowledge. That's a legitimate single axis, not a category error
— as long as we also report the *domain* axis REV wants.

**DOL → SMR:** Granting SMR's amortization point, but I'll counter: the "cheap at inference"
property of RLHF/CAI is exactly why it's *dangerous* operationally — once knowledge is baked into
weights you **cannot inspect or hot-patch it**. With code-as-policy I can `git diff` the reward and
the safety gate, review it, and roll it back. So the efficiency axis and the interpretability axis
are coupled: code-as-policy trades runtime cost for **auditability and reversibility**.

## Round 3 — synthesis

Points of consensus the doc must encode:

1. **The unifying frame is "where does normative knowledge live"** (RLE/SMR), but it MUST be paired
   with a **domain-of-applicability** caveat (REV): code-as-policy needs a verifier; RLHF/CAI are
   built for the verifier-free regime (tone, harmlessness). State both.
2. **Verifiability is task-conferred, not method-conferred** (REV vs PSRE). The repo's hard,
   ground-truth reward exists because incident-response *has an oracle* (SLO recovery). Don't
   generalize it to all alignment.
3. **Name the mechanism precisely** (RLE, conceded by PSRE): code-as-policy here =
   *verifier-guided inference-time search over a frozen, swappable policy + a rejection safety
   gate*, NOT policy-gradient. RLHF = reward-model + PPO + KL. CAI = SL self-revision + RLAIF.
4. **Efficiency is amortized capex vs per-call opex** (SMR vs DOL): RLHF/CAI pay upfront in
   labels+GPU and are cheap per query; code-as-policy pays per-incident inference but needs no
   labels/training.
5. **Interpretability ↔ reversibility coupling** (DOL): weight-baked knowledge is opaque and hard
   to patch; code knowledge is `git`-diffable, reviewable, reversible.

These five become the spine of the essay; the 5-axis table is the artifact, with an explicit
honest "where code-as-policy LOSES" section to satisfy REV.
