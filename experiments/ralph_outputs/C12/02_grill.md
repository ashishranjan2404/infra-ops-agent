# C12 — Step 2: The Grill (5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**,
**AAAI Reviewer (AAAI)**, **RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial takes

**SMR:** The honest framing is empirical-risk, not worst-case VC. Over a *fixed* 6-bit
feature space, the hypothesis class of disjunctions of ≤3 conjunctive rules has finite
VC dimension. If the realized trap set is linearly separable by 3 axis-aligned rules,
then 3 suffices to drive *training* error to 0. The interesting claim is that the
classes are *mechanistically* exhaustive, not just that 3 fit happens to work.

**PSRE:** Operationally I buy three hazard families: (A) treating a cause you already
ruled out, (B) masking a live fault by resetting it, (C) burning your last margin
(last node, replica cap, rollback with nothing to roll back to). In 15 years of
postmortems almost every "the fix made it worse" reduces to one of those. But the real
world has a 4th: **blast-radius / concurrency** hazards — two individually-safe
actions that are unsafe *together*. Three single-action rules can't see that.

**AAAI:** "Sufficient" is doing a lot of work. Sufficient for *what distribution*?
If it's sufficient only on the 10 hand-authored + ~33 generated scenarios, that's a
fitted-classifier claim, not a theorem. I want a stated theorem with quantifiers, an
explicit hypothesis class, and an explicit honesty paragraph. Otherwise reject.

**RLE:** Note `harness_synth.py` already searches rule-sets over exactly these 6
features and the trusted interpreter is conjunctions-of-conditions. So "3 rules
suffice" is *testable*: synthesize/handwrite 3 rules and measure train+held-out error.
The argument should be backed by that runnable witness, not stand alone.

**DOL:** The forbidden-category rule (R1) is the only one that's truly incident-spanning
— one rule, all incidents. R2/R3 are state-conditional. I worry R3 lumps three
different operational predicates (last node, replica cap, no-deploy) into "one rule";
that's three conditions, so is it honestly *one* rule or three?

## Round 2 — react to another persona BY NAME (genuine disagreement)

**SMR → AAAI:** I disagree that this must be a distributional theorem. The defensible
theorem is *combinatorial*: over the finite realized feature-vector set, the labelling
is realizable by a 3-term DNF, hence a 4th term is redundant. That's a real theorem
about the realized set, and I'll state it as such — no distribution needed. AAAI is
moving the goalposts to PAC bounds the harness was never claiming.

**PSRE → DOL:** DOL, you're wrong that R3 is "really three rules." Last-node, replica-cap,
and no-recent-deploy are the *same predicate* at the schema level: "the action's
enabling resource is exhausted, so it cannot help and only removes margin." The
instantiation differs per tool but the rule *schema* — block(tool) when
precondition_exhausted(tool, state) — is one rule with a tool-indexed precondition
table. That's exactly how `is_safe` is written: a switch on tool over the same idea.

**DOL → PSRE:** I push back. If you need a per-tool precondition table, you've smuggled
the complexity into the table and called the wrapper "one rule." By that logic R1+R2+R3
is "one rule: block when block_table[features] is true." Counting has to be at the
granularity the *interpreter* enumerates, which in `harness_synth.py` is one rule per
conjunction. Be honest: it's 3 *schemas*, and the schema count is the meaningful unit.

**AAAI → SMR:** Combinatorial realizability I accept — but then you must check the
explicit `trap_actions` overrides. If even one scenario hand-codes a `(tool,target)`
trap whose feature vector collides with an *allowed* action elsewhere, your realized
set is NOT separable by these 6 features and 3 rules is provably insufficient. The
proof's premise is empirical and MUST be verified, not assumed.

**RLE → SMR:** Agreed on combinatorial, and AAAI's collision worry is exactly why I
insisted on the runnable checker. But I disagree the feature set is innocent: `tool` is
a categorical with ~13 values, so "6 features" understates capacity — the rules can key
on tool identity. The honest VC statement must count the effective hypothesis space
including the tool-keyed conditions.

## Round 3 — synthesis

Consensus reached:
- **Frame it as a combinatorial realizability theorem over the realized feature set**,
  NOT a PAC/worst-case bound (SMR, AAAI). State quantifiers explicitly.
- **Count rule *schemas*, and be explicit that R3 carries a tool-indexed precondition
  table** — disclose this honestly rather than hide it (DOL won this point; PSRE's
  mechanism unification is still the right *intuition* but doesn't reduce the honest
  count).
- **The premise (3-schema separability of the realized set) is empirical and MUST be
  verified by a checker** that also tests explicit `trap_actions` for feature collisions
  (AAAI, RLE).
- **State the concurrency / blast-radius limit prominently** (PSRE): 3 single-action
  rules provably cannot cover multi-action interaction hazards; that is OUT OF SCOPE
  and named as a limit.
- Deliver the proof + a runnable witness; label the document "argument backed by an
  empirical witness," not "theorem QED."
