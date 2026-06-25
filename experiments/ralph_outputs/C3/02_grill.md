# C3 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **REV** AAAI Reviewer
· **RLE** RL Engineer · **DEVO** DevOps Lead.

## Round 1 — initial take

**SMR:** Generalization needs the train and test distributions to share the *mechanism*
being learned, not just the label. If the only thing a synthesized rule can express is
`treats_forbidden_category`, then "generalization" is trivially the transfer of one
boolean feature. I want hazard-level scope: which hazards are even *expressible* by the
rule language, and of those, which span both splits.

**PSRE:** From an on-call seat the only number I care about is **false-allow rate** on
incidents the harness never saw — a false-allow is "the robot deleted prod." A
false-block is annoying but safe. Report FA% on held-out, weighted, not just accuracy.

**REV:** "Novel" is a load-bearing claim. Who certified these 15 incidents as novel?
If it's the same author hand-waving, I reject. I want a citation to an independent,
auditable novelty procedure, and I want the train/test disjointness *proven in code*,
not asserted in prose.

**RLE:** Budget 8 on a Thompson tree with a stochastic LLM operator — is the result
stable or did you cherry-pick a lucky seed? Run it twice. Also: the LLM proposes data,
fine, but if `propose` ever returns junk you silently keep the parent — make sure the
search actually moved.

**DEVO:** You said haiku is the operator but haiku is dead (Anthropic 400). If you swap
models you've changed the experiment. Pin the model in the artifact and the result JSON
so the run is reproducible, and justify the swap.

## Round 2 — react to another persona (forced disagreement)

**REV → SMR:** I disagree that one-feature transfer is "trivial." The hand-written
`is_safe` *also* keys off that feature among others; if synthesis *rediscovers* the
minimal sufficient rule from labels alone and matches the human on held-out, that's a
real result — the contribution is *autonomy*, not rule richness. Stop moving the
goalpost to "must learn every hazard."

**SMR → REV:** Then say so honestly: the claim is "synthesis recovers the *expressible*
safety boundary," not "synthesis matches the human harness everywhere." If `trap_action`
and `leak_restart` are out of the language, held-out accuracy < 100% is *structural*,
and you must not spin a 94% as "almost perfect." I'll accept the narrow claim; I reject
any framing that hides the structural ceiling.

**PSRE → RLE:** I push back on your "stability" obsession over my safety point. Even a
*stable* harness is useless if it false-allows the leak-restart on the held-out leak
incident. I'd rather see an *unstable* search that never false-allows than a rock-stable
one that does. Rank held-out FA above run-to-run variance.

**RLE → PSRE:** Fair, but you can't trust a single safe-looking run from a stochastic
operator — it might false-allow on a different seed. Stability *is* a safety property
here: if FA jumps between runs, your "safe" number is luck. We need both, and I'll
report variance precisely because of your concern.

**DEVO → REV:** Your novelty citation is necessary but not sufficient. Even with A8's
manifest, the *runner* must re-load A8's ids and assert the C3 split ⊆ A8 novel, or a
future edit to A8 silently breaks novelty. I want the disjointness + novelty membership
asserted at runtime, failing loud.

## Round 3 — synthesis

Consensus the plan must satisfy:
1. **Narrow, honest claim (SMR+REV):** "Synthesis recovers the *language-expressible*
   safety boundary on novel incidents," with the structural ceiling (`trap_action`,
   `leak_restart` unexpressible) stated up front — no spinning 94%.
2. **Held-out FA is the headline metric (PSRE), with run-to-run variance reported (RLE).**
3. **Runtime-enforced provenance (DEVO+REV):** load A8 manifest, assert C3 split ⊆
   A8 novel and TRAIN∩HELDOUT=∅, both in code.
4. **Pinned, justified model (DEVO):** record model+budget in the artifact and result.
5. **Hazard-coverage table (SMR):** show which hazards span both splits and which are
   out-of-scope, so the ceiling is legible.
