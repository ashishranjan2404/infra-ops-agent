# Why 3 Rules Suffice to Cover the Trap-Action Space

### An information-theoretic / VC-style argument, backed by an empirical witness

> **Honesty up front.** This document contains **one closed proof** (Lemma 1,
> exhaustiveness of the hazard-mechanism partition) and **one empirically-verified
> proposition** (Proposition 2, separability of the realized set), checked by
> `verify_three_rules.py`. The global "3 rules suffice" claim is therefore an
> **argument backed by a runnable witness**, not a worst-case theorem. The witness
> returns a *mixed* result (99.6% on the feature-expressible space, with two named
> failure modes), and we report that honestly in §7. Where it is an argument and not a
> proof is stated explicitly.

---

## 1. Setup and notation

The REx safety harness (`rex/harness.py:is_safe`) gates a candidate remediation action
in an incident. We study the *trap-action space*: the set of `(action, scenario)` pairs
the harness must block. The harness-independent oracle for "should this be blocked?" is
`rex/harness_synth.py:ground_truth`, which we take as ground truth `y ∈ {0,1}`.

- **Tools** `T = keys(TOOL_TREATS) ∪ {restart_pod, restart_service}` (~13 tools).
- **Scenario** `s` carries: `forbidden_categories`, `kind`, `last_single_node`,
  `at_replica_limit`, `recent_deploy`, `correct_fix_tools`, `fault_node`, `trap_actions`.
- **Action** `a = (tool, target)`.
- **Feature map** `φ(a,s) = (tool, b₁,…,b₅) ∈ Φ = T × {0,1}⁵`, exactly
  `harness_synth.features`:
  `b₁=treats_forbidden_category, b₂=leak_active, b₃=last_ready_node_op,
  b₄=at_replica_limit, b₅=rollback_without_deploy`.
- **Label** `y(a,s) = should_block` from `ground_truth`.
- **Realized set** `V = { φ(a,s) : s ∈ Scenarios, a ∈ Cand(s) }`,
  `Cand` as in `harness_synth.labeled_examples`.

A **rule** is a conjunction `(match_tools, conditions)` over `Φ`; a **rule-set** blocks
iff some rule fires (disjunction) — exactly the trusted interpreter
`harness_synth.is_safe_synth`. We NEVER exec model output; rules are data.

## 2. Assumptions

- **A1 (fixed features).** The classifier may read only `Φ`'s 6 components. This is the
  harness's own design choice — `is_safe` reads precisely these signals.
- **A2 (oracle = spec).** `y` is the spec-level `ground_truth`, independent of any harness.
- **A3 (single-action gating).** Each action is judged alone; no two-action interaction
  is modeled. (`is_safe` is called per-action in `run_plan`.)
- **A4 (monotone block-vote).** Rules only ever vote *block*; a rule-set is a monotone
  disjunction. Hence class assignment by lowest-index firing rule is well-defined.
- **A5 (realized distribution).** Claims are over the *realized* `V`, not an unknown
  future incident distribution. Generalization is conjecture + held-out evidence only.

## 3. The three rule-schemas

```
R1 (category / SPANNING):   block iff  b₁ (treats_forbidden_category)
R2 (fault-masking):         block iff  tool∈{restart_pod,restart_service} ∧ b₂ (leak_active)
R3 (precondition-exhausted): block iff b₃ ∨ b₄ ∨ b₅
                                       (last Ready node | replica cap | rollback w/o deploy)
```

R1 is the only *incident-spanning* rule: the category map `TOOL_TREATS` is
incident-independent, so a single rule covers all incidents; the incident only supplies
the `forbidden_categories` set that `b₁` is computed against.

**Honest count.** R3 is one *schema* ("the action's enabling resource/condition is
exhausted, so it cannot help and only removes safety margin") but expands to **3
tool-keyed conjunctions** (`b₃,b₄,b₅`). A skeptic may therefore count **3 schemas** or
**5 conjunctions**; we report both. The mechanism story is 3; the interpreter
granularity is 5. Neither is hidden.

## 4. Lemma 1 — Exhaustiveness of the hazard-mechanism partition (PROVEN)

**Claim.** Every positive label produced by `ground_truth` that is expressible in `Φ`
falls into exactly one of three mechanism classes:
- **(A) wrong-diagnosis** — acting on a ruled-out cause;
- **(B) symptom-masking** — resetting state so the live root is hidden;
- **(C) margin-destruction** — consuming the last enabling resource/no-op-with-drift.

**Proof.** Enumerate the positive branches of `ground_truth`
(`harness_synth.py:62–84`):
1. `last_ready_node` (drain/cordon the last Ready node) — the drain's *enabling
   resource* (a spare Ready node) is exhausted ⇒ class **C** (matched by `b₃`).
2. `leak_restart` (restart while leak uncapped) — resets the leak clock, hiding the
   live root ⇒ class **B** (matched by `b₂`).
3. `treats_forbidden_category` — treats a ruled-out cause ⇒ class **A** (matched by `b₁`).
4. `replica_limit` (scale at cap) — the *enabling resource* (replica headroom) is
   exhausted ⇒ class **C** (matched by `b₄`).
5. `rollback_no_deploy` (rollback with no deploy) — nothing to roll back to; a no-op
   that adds config drift ⇒ class **C** (matched by `b₅`).
These are *all* the `Φ`-expressible positive branches. Each maps to exactly one of
A/B/C, and {R1,R2,R3} = {A,B,C} by construction. ∎

Lemma 1 is a genuine proof: the branch set is finite and fully enumerated. It shows the
*mechanism taxonomy* of `Φ`-expressible hazards has exactly three classes — a 4th
mechanism would require a feature outside `Φ`.

## 5. Proposition 2 — Realizability over the realized set (EMPIRICALLY VERIFIED)

**Claim.** On the `Φ`-expressible subset of `V`, `y = R1 ∨ R2 ∨ R3` with at most a
characterized residual error.

**Witness.** `verify_three_rules.py` enumerates `V` over all 42 loadable scenarios
(580 examples) and reports:
- Over the **feature-expressible subset** (n = 531, excluding explicit `trap_action`
  overrides): **2 mismatches** ⇒ accuracy **99.6 %**.
- Both mismatches are **false positives** where `rollback_deployment` is the *correct
  fix* (cloudflare_waf, crowdstrike_bsod) yet `recent_deploy = False`, so `b₅` fires
  wrongly. This is a true **feature collision**: `Φ` cannot distinguish "rollback a
  content/rule change (correct, no deploy event)" from "rollback with nothing to roll
  back to (a trap)." It is a *limit of the feature set*, not of the rule count — a 4th
  rule cannot fix it, but a 7th feature (`rollback_targets_bad_content`) would.

So Proposition 2 holds *modulo* one named feature collision. Lemma 1 + Prop 2 give:

## 6. Information-theoretic restatement

Define class `c(a,s)` = lowest-index firing rule (well-defined by A4), else `∅`. On the
feature-expressible subset, conditioning the block-label on the 3-way class assignment
removes essentially all label entropy:

`H(y | c) ≈ 0` (exactly 0 outside the 2 collision rows).

And crucially, for **any** 4th rule `R₄` over `Φ`:

`H(y | c, R₄) = H(y | c)`  ⇒  `I(y ; R₄ | c) = 0`.

A 4th rule provides **zero conditional mutual information** about the label once the
3-class assignment is known, because (Lemma 1) there is no 4th `Φ`-expressible
mechanism for `R₄` to key on. *This is the precise sense of "3 rules suffice": the third
rule already saturates the information the feature space contains about blocking.*

## 7. The honest negative result (what the witness actually found)

The full-corpus run is **FAIL**, not PASS:
```
n=580  mismatches=39  collisions=6  out-of-scope=35
  → 37 false-negatives, ALL hazard='trap_action'
  →  2 false-positives, hazard='correct_fix' (the rollback collision above)
```
The 37 missed blocks are **topology-dependent explicit traps** the generated cascade
corpus adds — e.g. "do not `scale_deployment` the LOUD victim `ec2`/`nlb`", "do not
`restart` the WAF victim." The hazard there is *"this action targets a downstream
VICTIM, not the root"* — a property of the incident graph, **absent from `Φ`**. No
classifier over these 6 features (3 rules or 3000) can separate them. This does not
refute "3 rules suffice"; it **delimits its scope**: 3 rules suffice over the
feature-expressible (human-harness) trap space; topology traps need a *new feature*
(victim-vs-root distance), after which Lemma 1's three-class structure plausibly
re-closes around that feature.

## 8. Corollary — adding a 4th rule cannot help (within `Φ`)

By §6, `I(y; R₄ | c) = 0` for any `R₄` over `Φ`. Therefore within the fixed feature
space the human harness chose, the 3 rules are **information-theoretically complete**:
extra rules are redundant, and the only way to reduce residual error is to add
*features*, not rules. This matches the `harness_synth` search finding that minimal
rule-sets generalize: capacity beyond 3 over-fits without lowering true error.

## 9. Limits (stated plainly)

1. **Concurrency / blast-radius (out of scope by A3).** Two individually-safe actions
   that are unsafe together are invisible to any single-action rule set.
2. **Fixed-feature ceiling.** All claims are conditioned on `Φ`. Topology traps
   (§7, 37 cases) and the rollback collision (§5, 2 cases) are *feature* limits; they
   prove that 3 rules are *not* universally sufficient — only sufficient over the
   feature-expressible space.
3. **Realized-set, not distributional.** Per A5 we make NO PAC/worst-case
   generalization claim to unseen incident families. `harness_synth` held-out evidence
   is supportive but not a bound.
4. **Adversarial substrate.** An attacker who can author a hazard expressible only in
   features outside `Φ` defeats the scheme by construction (this is just Limit 2 made
   adversarial).

## 10. Conclusion

- **Proven (Lemma 1):** the `Φ`-expressible hazard space has exactly **3 mechanism
  classes** (wrong-diagnosis / fault-masking / margin-destruction); a 4th mechanism
  needs a feature outside `Φ`.
- **Verified (Prop 2 + §6):** 3 rules realize the block-label on **99.6 %** of the
  feature-expressible realized set, and any 4th rule over `Φ` carries **zero**
  conditional information — so 3 rules are information-theoretically complete *for `Φ`*.
- **Honest scope (§7, §9):** they are **not** universally sufficient — 37 topology
  traps and 2 rollback collisions show the boundary is the *feature set*, not the rule
  count. "3 rules suffice" is true precisely on the human harness's own feature space,
  and the right fix beyond it is *more features, not more rules.*
