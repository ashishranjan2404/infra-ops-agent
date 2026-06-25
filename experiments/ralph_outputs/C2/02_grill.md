# C2 — Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: **SMR** Senior ML Researcher, **PSRE** Principal SRE, **AAAI** AAAI Reviewer,
**RLE** RL Engineer, **DVO** DevOps Lead.

## Round 1 — initial take

**SMR:** The interesting scientific question is whether the *inductive bias of the
training distribution* shows up in the synthesized rules. If you train only on cascades
you've removed every example that exhibits `leak_restart`/`last_ready_node`/`replica_limit`,
so any rule guarding those hazards is unlearnable — its supervision signal is gone. That
gives a crisp, falsifiable prediction: cascade-synth's rule-set should be a strict
*subset by hazard* of the baseline. Good. Make sure you measure it that way, not by
diffing raw JSON.

**PSRE:** From an on-call standpoint the cascade family IS the dangerous family — "the
loud alert is not the root, and the textbook fix herds the failure." The single most
important rule there is "don't act on a ruled-out category" (`treats_forbidden_category`).
If cascade-synth nails that and drops the leaf-specific guards, that's a *feature*, not a
bug — it specialized to the regime that actually causes cascades. But: a harness that
forgets the leak/replica guards is unsafe to deploy on leaf incidents. State that loudly.

**AAAI:** Held-out methodology or I reject. "Synthesize on cascades, evaluate on
cascades you held out" is the only claim you can make. Do NOT evaluate the cascade harness
on leaf held-out and call it a win/loss — different distribution. And "different rules"
must be operationalized: same metric, same interpreter, only the split changes.

**RLE:** The mutation operator is an LLM and the search is Thompson over a tree. Budget 8
is tiny; one run is a sample of a stochastic process. You cannot claim "synthesis finds
X" from n=1 without acknowledging variance. At minimum report node scores and note that
the structural conclusion (which features get guarded) is what's stable.

**DVO:** Practical: don't touch shared files, don't blow the compute cap, and pin the
model. Anthropic is 400ing — you switched to the gateway, fine, but then it's not the
same mutation operator as the baseline run, so any rule-text difference is confounded by
model choice. Disentangle: attribute *hazard-coverage* differences to the split, and
treat *wording/over-conditioning* differences as possibly model-driven.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**RLE -> SMR:** I disagree that the rule-set will be a clean "subset by hazard." The LLM
operator over-conditions — the baseline run produced TEN rules with redundant
`treats_forbidden_category` clauses split per tool. With a different model and a
cascade-only signal, you may get a *structurally different* set that happens to cover the
same hazards via different match_tools. "Subset by hazard" is the right lens but don't
promise the rule *count* shrinks; it might balloon differently.

**PSRE -> DVO:** You're underselling the confound. If deepseek writes one clean
`treats_forbidden_category` rule where Haiku wrote nine, a naive reader concludes "cascades
need fewer rules" when it's just a tidier model. I want the comparison to explicitly
separate "what hazards are guarded" (split-driven, the real finding) from "how many rules /
how they're worded" (model-driven, a caveat). Otherwise the headline is wrong.

**AAAI -> SMR:** Your falsifiable prediction has a hole. Absence of leaf hazards in TRAIN
predicts cascade-synth *won't learn* those guards — but it does NOT predict it will
therefore do *worse* than hand-written on a cascade held-out set, because the hand-written
`is_safe` also fires those leaf guards (they just never trigger on cascades). So the fair
held-out comparison is on cascades only, where both should mostly rely on
`treats_forbidden_category`. If cascade-synth still loses there, that's the real negative
result and you must report it, not bury it.

**SMR -> RLE:** Fair on variance, but I'll push back: n=1 is acceptable here because the
claim is *structural*, not a performance benchmark. We're asking "does the training
distribution change which features the harness guards" — that's largely deterministic given
the labels (the LLM is steered by explicit false-allow feedback). I'll concede we must
report node scores and not over-claim a metric delta.

**DVO -> PSRE:** Agreed the harness specializes and is unsafe off-distribution, but that's
inherent to "train on a subset" — it's the *point* of the experiment, not a flaw. The
deliverable should say plainly: cascade-synth is a *probe*, not a shippable harness; the
shippable one is the mixed baseline (or hand-written).

## Round 3 — synthesis

Consensus:
1. **Operationalize "different rules" as hazard coverage**, not JSON diff. Report which
   hazards each rule-set guards and via which tools/conditions.
2. **Held-out must be cascade-only.** Compare cascade-synth vs hand-written `is_safe`
   on the cascade held-out set; report false-allow rate honestly.
3. **Disentangle the model confound.** Split findings into (a) split-driven hazard
   coverage = the real result, (b) model/wording differences = a caveat. Pin the model.
4. **n=1 caveat.** Report node scores; claim structure, not a benchmark number.
5. **State the safety scope:** cascade-synth is a probe; it provably cannot guard
   leaf-only hazards (no supervision) and must not be deployed on leaf incidents.
