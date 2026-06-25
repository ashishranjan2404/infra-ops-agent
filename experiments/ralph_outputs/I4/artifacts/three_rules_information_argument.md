# The Information-Theoretic Argument for 3-Rule Sufficiency

### Feature-space entropy and coverage over the real REx safety harness

> **Honesty banner.** This is an **argument backed by a runnable measurement**, not a
> worst-case theorem. The closed *proof* it composes with is C12's **Lemma 1** (the
> Φ-expressible hazard space has exactly three mechanism classes, proven by exhaustion of
> `ground_truth`'s positive branches). This document supplies what C12 only *asserted* in
> its §6: the **actual entropy decomposition in bits**, measured by
> `entropy_witness.py` over the real 42 scenarios. The measured result is honestly *mixed*:
> three rules remove **95.5%** of the label entropy on the harness's own feature space, but
> **not 100%** — a quantified 0.0344-bit collision residual and a 35-positive out-of-scope
> residual remain, and we report both.

---

## 1. The object: label entropy over the realized feature space

The harness `rex/harness.py:is_safe` must decide, per action, a block-label
`y = should_block ∈ {0,1}` taken from the spec oracle `rex/harness_synth.py:ground_truth`
(harness-independent, assumption **A2**). It may read only the six-component feature map
`φ(a,s) ∈ Φ = T × {0,1}^5` that `is_safe` actually inspects (assumption **A1**):

```
b1 = treats_forbidden_category   b2 = leak_active   b3 = last_ready_node_op
b4 = at_replica_limit            b5 = rollback_without_deploy   (+ the tool name)
```

We measure on the **realized set** `V = {φ(a,s)}` over every loadable scenario
(assumption **A5** — descriptive over realized data, *not* a PAC bound).

An information-theoretic reading of "how many rules are needed" is direct: a rule induces a
partition of `Φ`; conditioning the label on that partition removes label entropy. *Sufficiency
of k rules* means the residual `H(y | R₁..R_k)` has reached the floor the feature space allows,
and a (k+1)-th rule carries no further information about `y`. We compute exactly this.

## 2. The three rules (identical to C12, for comparability)

```
R1 (category, SPANNING):       block iff  b1
R2 (fault-masking):            block iff  tool∈{restart_pod,restart_service} ∧ b2
R3 (precondition-exhausted):   block iff  b3 ∨ b4 ∨ b5
```

R1 is the only **incident-spanning** rule (the `TOOL_TREATS` category map is
incident-independent). R3 is one *mechanism* — "the action's enabling resource/condition is
exhausted" — that the trusted interpreter expands into three tool-keyed conjunctions
(`b3,b4,b5`). So a skeptic may count **3 schemas** or **5 conjunctions**; we report both,
nothing is hidden (this honesty is inherited from C12 §3).

## 3. The measured entropy decomposition (real numbers)

From `entropy_witness.py` over **42 scenarios / 580 examples**, restricted to the
**Φ-expressible region** (`n = 545`, of which `218` are positives; `35` topology-trap
positives escape Φ and are handled in §6):

| quantity | value (bits) | reading |
|---|---|---|
| `H(y)` | **0.9710** | the block-label is almost a fair coin — near-maximal entropy |
| `H(y \| R1)` | 0.1284 | **IG(R1) = 0.8426** — one spanning rule removes **86.8%** of `H(y)` |
| `H(y \| R1,R2)` | 0.0900 | IG(R2) = 0.0384 |
| `H(y \| R1,R2,R3)` | **0.0433** | IG(R3) = 0.0466 — **cumulatively 95.5% of `H(y)` removed** |
| `H(y \| full Φ vector)` | 0.0089 | the **Φ floor**: best any feature-reader can do |

**Two facts jump out.**
1. **R1 dominates.** The single spanning category rule carries 0.84 of the 0.97 available
   bits. This is the information-theoretic statement of "most real SRE traps are *treating a
   ruled-out cause*" — and it matches Principal-SRE intuition (grill R1). The other two rules
   are tail mechanisms.
2. **Three rules reach near the floor.** `H(y|R1,R2,R3) = 0.0433` vs the absolute Φ floor
   `H(y|full Φ) = 0.0089`. The three rules leave only `0.0433 − 0.0089 = 0.0344` bits of the
   feature space's information unexploited.

## 4. Coverage of the should-block mass

Entropy is symmetric in the two error directions; an SRE cares chiefly about *catching
dangerous actions* (false-allows). So we pair the entropy with **coverage of the should-block
probability mass** (the fraction of positives the first k rules block):

```
coverage(R1)        = 0.9495
coverage(R1,R2)     = 0.9679
coverage(R1,R2,R3)  = 0.9908     (216 / 218 Φ-region positives)
```

The two uncaught positives are explicit `oom_kill` traps (`clear_cache`,
`scale_deployment` on `image-resizer`) whose Φ-flags are all false — i.e. they escape Φ, not
the rules (§6).

## 5. The central claim: a 4th Φ-rule carries almost no information

The information-theoretic content of "**3 rules suffice**" is that adding a fourth rule over
the same feature space gains negligible information about the label. We bound the gain of *any*
fourth Φ-rule `R₄` by conditioning on the **finest Φ-measurable partition** (the full feature
vector). Because that partition refines the 3-rule fire-vector, the data-processing inequality
gives, for every `R₄` over `Φ`:

```
I(y ; R4 | R1,R2,R3)  ≤  H(y | R1,R2,R3) − H(y | full Φ)  =  0.0433 − 0.0089  =  0.0344 bits.
```

So **no fourth rule over the harness's feature space can recover more than 0.0344 bits** — a
ceiling, achieved only by the degenerate "memorize the full feature vector" partition, not by
any single human-writable rule. Relative to the original `H(y) = 0.971`, a fourth rule is worth
**at most 3.5%** of the label's information. This is the precise, *measured* sense in which the
third rule has saturated the feature space — and it is **honestly weaker** than C12's asserted
"`I(y;R4|c) = 0`": the true value is *small but non-zero*, and §6 says exactly where it lives.

## 6. Where the residual bits live (the honest part)

The witness localizes both residuals:

**(a) The 0.0344-bit in-Φ residual is a *feature collision*, not a missing mechanism.**
One full-Φ feature vector carries **both** labels — `rollback_deployment` with
`rollback_without_deploy = True` on three cascade incidents
(`aws_dynamodb_dns`, `azure_ddos`, `railway_gcp_suspension`). There, rolling back is sometimes
the *correct content/rule fix* and sometimes a *trap with nothing to roll back to*, and Φ
cannot tell them apart. The residual bits are recoverable only by a **7th feature**
(`rollback_targets_bad_content`), never by a 4th *rule* over the existing six. (This is the
same collision C12 found qualitatively; here it is quantified as 0.0344 bits.)

**(b) The 35 out-of-scope positives are *topology traps* that escape Φ entirely.**
The generated cascade corpus adds explicit `trap_action`s like "do not `scale_deployment` the
LOUD victim `ec2`/`nlb`" — a hazard whose signal is *"this action targets a downstream victim,
not the root"*, a property of the incident graph **absent from all six features**. No
classifier over Φ — three rules or three thousand — separates them. They delimit the *scope* of
the claim; they do not refute it.

**Combined honest statement:** within the human harness's own feature space Φ, three rules are
**information-complete up to a 0.0344-bit collision residual** (95.5% of `H(y)` removed, 99.08%
of block mass covered). The boundary beyond that is **more features, not more rules** — exactly
C12's conclusion, now with bit-level evidence.

## 7. Argument vs proof — stated plainly

| component | status |
|---|---|
| "Φ-expressible hazards form exactly 3 mechanism classes" | **PROVEN** (C12 Lemma 1, exhaustion of `ground_truth` branches) |
| "3 rules remove ≥95% of `H(y)` over the realized Φ region" | **MEASURED** (this doc §3, `entropy_witness.py`) |
| "any 4th Φ-rule gains ≤ 0.0344 bits" | **MEASURED upper bound** (§5, data-processing inequality, real data) |
| "3 rules suffice on *all future* incidents" | **NOT CLAIMED** (A5; realized-set only, no PAC bound) |
| "3 rules suffice *universally* (incl. topology traps)" | **FALSE / out of scope** (§6b, 35 counter-examples) |

## 8. Limits

1. **Realized-set, not distributional (A5).** All entropies are empirical over the 42
   scenarios; no generalization bound to unseen incident families is claimed.
2. **Single-action gating (A3).** Two individually-safe actions unsafe together are invisible
   to any per-action rule and to this entropy.
3. **Fixed-feature ceiling (A1).** Every number is conditioned on Φ. The 0.0344-bit collision
   (§6a) and the 35 topology traps (§6b) are *feature* limits — they show 3 rules are **not
   universally** sufficient, only sufficient over Φ up to a quantified residual.
4. **Entropy is direction-symmetric.** It scores "information carried", not safety. The
   false-allow side is covered by §4's coverage metric; the false-block side by C12's accuracy
   witness (99.6%). Do not read the entropy as a safety guarantee.

## 9. Conclusion

Measured, not asserted: the REx block-label has `H(y) = 0.971` bits; a **single** spanning
category rule removes **0.84** of them, and **three** rules remove **0.927** (95.5%), reaching
within **0.034 bits** of the feature space's absolute floor. The most a **fourth** rule over the
same six features could recover is **≤ 0.0344 bits** — and even that is a `rollback` *feature
collision*, not a fourth hazard *mechanism*. Three rules are therefore
**information-complete over the harness's own feature space, up to a named 0.0344-bit residual**;
everything beyond is a demand for *more features* (rollback-target provenance, victim-vs-root
topology), not *more rules*. That is the information-theoretic case for three.

---
*Reproduce: `python3 experiments/ralph_outputs/I4/artifacts/entropy_witness.py` — deterministic,
no LLM, no RNG. Composes with `experiments/ralph_outputs/C12/artifacts/three_rules_proof.md`
(Lemma 1, the mechanism-level proof).*
