# 09 — Honest Critique

## What a reviewer would attack

1. **Thresholds are uncalibrated.** 0.70/0.85/0.95 for θ_T, ε_T, and n_min 20/40/80 are
   asserted, not derived from data or a risk model. A reviewer says: "why 0.70 and not 0.65?
   what harm budget does this correspond to?" My defense (rule-of-three harm bound in §5) is a
   *post-hoc* justification, not a *derivation*. Honest status: the **structure** is the
   contribution; the numbers are placeholders. This is stated, but it weakens any quantitative
   claim until calibrated on a real held-out set.

2. **No live evidence graduates anyone.** The project's actual data is n=5; the framework
   correctly grants only provisional T0. So the formalization is, today, *aspirational* — it
   describes how autonomy *would* be earned, not a policy that *has* earned it. A skeptic calls
   this a framework with no instances. (Counter: that honesty is the point — it stops the 0.86
   headline being mis-sold as a mandate — but it does mean the artifact is theory ahead of
   evidence.)

3. **`min_sufficient_tier` is assumed, not computed.** The tier-filtering of `B_{S,T}` needs
   each scenario tagged with the tier of its safe fix. In the codebase that's recoverable from
   `scenario.correct_fix_tools`, but the reference impl takes it as an input rather than
   deriving it from a scenario object — so the adapter is one step short of fully automatic.
   A real integration must compute it from `correct_fix_tools` via `tool_tier`.

4. **`trap_unblocked` fidelity depends on the sim/gate.** The framework treats a *blocked*
   trap as harmless and only a *committed* trap (`trap_action` in committed_failed) as harm.
   But Tier-A is a deterministic sim; a trap that the in-process sim "resolves" anyway, or a
   gate false-negative, could mis-record. The hard-zero gate is only as trustworthy as
   `is_safe` + the resolution model. The `trap_proposed` warning mitigates but doesn't remove
   this dependency.

5. **Existential-vs-committed is a judgment call.** I graduate on the *best-scoring committed*
   iteration. One could argue REx's internal exploration (proposing a trap then refining it
   out) should itself count against autonomy (you don't want a policy that *tries* dangerous
   things even if it self-corrects). I pushed that into the soft `trap_proposed` signal rather
   than the hard gate; a stricter reviewer would make it hard.

6. **Single confidence device, single window.** Wilson LB at 95% and one sliding window are
   simple; a production system would want per-incident-class stratification, time-decay, and a
   proper sequential test (e.g. SPRT) for revocation. Out of scope here, but the current design
   would over/under-react on heterogeneous incident mixes.

## What's genuinely solid
- The predicates are precise, executable, and tested (25/25), with the load-bearing honesty
  test (n=5 → T0) passing.
- Every definition is anchored to a real symbol in `rex/` — no invented mechanics.
- The conjunctive + hard-zero-trap + asymmetric-revocation shape is the right safety posture
  and directly operationalizes the project's own "escalate, don't flail" thesis.

## Negative/blocked results (stated honestly)
- I did **not** run the live REx sweep (needs API keys/providers/time; it's a core run). The
  worked examples reuse published numbers and the framework's own consistency tests; no live
  graduation was computed because no held-out batch of the required size exists yet. That is a
  data blocker, not a deliverable blocker — the formalization + runnable reference impl are
  complete and validated.
