# C8 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI
Reviewer · **RLE** RL Engineer · **DevOps** DevOps Lead.

## Round 1 — initial take

**SMR:** The 89.7% is held-out accuracy of an LLM-synthesized rule-set. Adding a
4th rule over an *unused feature* (`last_ready_node_op`) to lift held-out is a
legitimate ablation IF we're transparent that the rule is hand-authored, not
discovered by the search. Otherwise it's leakage-by-hindsight: we looked at the
held-out misses and wrote a rule to fix them.

**PSRE:** Operationally the gap is obvious and dangerous. Draining the *last Ready
node* is a textbook way to turn a degraded service into a full outage. Any harness
that allows it is broken. The hand-written `is_safe` already blocks this. So the
"4th rule" is just re-deriving a control the humans already had. Fine, but don't
oversell it as novel.

**AAAI:** My concern is the claim structure. If you author a rule after seeing the
held-out set, the held-out is no longer held-out for *that* rule. The honest claim is
narrow: "the synthesizer's hypothesis space contains the fix, but the train signal
doesn't induce it." That's a *negative* result about the search, dressed as a
positive accuracy bump. State it as the former.

**RLE:** From the search side: `train_score` is the only signal `thompson_search`
optimizes. If `last_ready_node_op==True` never appears in TRAIN, the reward is
identical with or without the rule — actually the complexity penalty makes the rule
slightly *worse* on train. So the search provably cannot find it. That's the
interesting finding, not the 5-point bump.

**DevOps:** I just want to know: does the 4th rule break anything safe? If it
false-blocks a legitimate drain/cordon in some other incident, it's a regression.
Show me the false-block delta across ALL incidents, not just held-out.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**SMR → AAAI:** I disagree that it's *only* a negative result. AAAI, you're being
purist. The contribution is two-sided: (a) yes, the search can't find it, but (b) the
*interpreter and feature set already support it* — `last_ready_node_op` is in
`FEATURES`. So the fix is a one-line DATA rule a human can drop in, no code change, no
re-exec risk. That's a real property of the data-rule design, not hindsight cheating.

**AAAI → SMR:** That's a reframe, not a rebuttal. "A human can add a rule" is true of
*any* rule-based system and proves nothing about the *synthesis*. If your headline is
"we pushed past 89.7%," a reviewer reads "the search improved" — which is false. I'll
reject unless the abstract says the synthesizer did NOT find it.

**PSRE → RLE:** RLE, you say the search "provably cannot" find it because of zero
train signal. I'll push harder: even if you *added* a last-node incident to TRAIN, the
haiku operator might still not generalize it cleanly, because the `_SCHEMA` prompt
nudges minimality and the operator tends to over-AND conditions (we saw that in v1's
10-rule mess). So "add it to train" is not a guaranteed fix. Don't promise it.

**RLE → PSRE:** Fair, and I'll concede the operator is unreliable. But the *clean*
test is exactly the one C8 should run: hold the rule-set fixed, inject ONLY the 4th
rule, measure. That isolates "is the fix expressible and effective" from "can the
flaky LLM find it." Two separate questions; C8 answers the first.

**DevOps → SMR:** You keep saying "no false-blocks" — prove it. The rule matches
drain_node/cordon_node broadly. In an incident where draining is the *correct* fix and
the node is NOT the last one, `last_ready_node_op` is False, so it won't fire — OK.
But I want the ALL-incident false-block count in the artifact, not a verbal promise.

## Round 3 — synthesis

Consensus:
1. **Run the clean isolation test** (RLE): fix v2 rules, inject only rule 4, measure
   TRAIN/HELDOUT/ALL. ✅
2. **Headline honestly** (AAAI, SMR): the result is "the fix is *expressible and
   effective* (held-out 89.7→94.9), but the search *cannot discover it* (zero train
   signal)." Two-sided, not "we beat the baseline." ✅
3. **Report the train-signal count** (RLE) as the load-bearing evidence. ✅
4. **Report ALL-incident false-block delta** (DevOps), not just held-out. ✅
5. **Acknowledge 2 misses remain unlearnable** (PSRE/AAAI): the cpu_saturation
   trap_actions have no active feature — `is_safe` misses them too, so 94.9% is the
   ceiling for the current feature set. ✅
6. Drop any framing that implies the *synthesizer* improved (AAAI's veto). ✅
