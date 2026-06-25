# D3 — 02 Grill (Ralph Loop, 5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (SRE)**, **AAAI Reviewer (REV)**,
**RL Engineer (RLE)**, **DevOps Lead (DVO)**.

## Round 1 — initial take

**SMR.** The mechanism is textbook GRPO. Advantage `A_i = r_i - b`, baseline `b`. If `b`
is the mean over a *mixed* group, then `b = E_S[E[r|S]]` and the advantage for a rollout on
an easy scenario stays positive even when that rollout is the *worse* one for its scenario.
By the law of total variance, `Var(r) = E[Var(r|S)] + Var(E[r|S])`. Same-scenario grouping
sets `b = E[r|S=s]`, killing the `Var(E[r|S])` between-scenario term. That term is pure
nuisance variance — it carries no information about *which rollout was better*. Reducing the
advantage's second moment directly reduces the per-sample policy-gradient variance.

**SRE.** From an incident-response standpoint I care that the scenarios are genuinely
different incidents (cache stampede vs disk-fill vs cert-expiry). If you mix them in a group,
the model gets rewarded for "this looked like an easy incident" not "this was the right
remediation." Same-scenario grouping is the right unit. But: are there enough rollouts PER
scenario to form a stable baseline? G=6 is small.

**REV.** Claim must be falsifiable. "Reduces gradient variance" — show me the estimator and
a number, not a vibe. Also: is this actually the *cause* of the flat baseline, or just one of
three confounded fixes? If you ship it alone you can't attribute the gain. I want an ablation
or at least an isolated mechanism demo.

**RLE.** Implementation reality: in HUD, `ts.run(group=G)` over a multi-task taskset — does a
group actually span tasks, or does HUD already group within-task? If HUD already keeps groups
within a single task, this whole fix is a no-op and we're solving a phantom. Must verify the
semantics before claiming a fix.

**DVO.** A live GRPO run needs the forked slug, the Tinker endpoint (which throws 502s), and
~30 min. That's over the compute cap and flaky. Whatever we ship must be runnable and provable
WITHOUT the live trainer, or it's not reproducible in CI.

## Round 2 — react to another persona BY NAME (forced disagreement)

**RLE → SMR (disagree).** SMR, your math is clean but you're assuming the bug exists. I pushed
on the HUD semantics: I am NOT convinced `ts.run` mixes scenarios within a group. The v2
docstring itself hedges — it says "(likely)". If HUD groups per-task internally, your beautiful
total-variance argument describes a problem we don't have. We cannot claim a "fix" for an
unconfirmed bug. At most we ship a *defensive* loop that GUARANTEES same-scenario groups
regardless of HUD's internal behavior.

**SMR → RLE (partial concede).** Fair hit. I'll downgrade the claim: instead of "this fixes
the flat baseline" I'll say "this *guarantees* the same-scenario invariant, and here is the
variance the invariant removes *if* groups were mixed." The defensive loop is correct either
way — if HUD already groups per-task, our per-scenario loop is just an explicit no-op with
zero downside. The variance math stands as the justification for *why the invariant matters*.

**REV → DVO (disagree).** DVO, "runnable without the trainer" is necessary but you're letting
us off too easy. A synthetic demo with hand-picked difficulties can show ANY reduction factor
I want. That's not evidence, it's set dressing. If you can't run the real GRPO, the demo must
at least be GROUNDED in the real reward statistics — use the ~0.5 mean / ~0.17 spread the v2
run actually logged, not invented numbers.

**DVO → REV (concede + push back).** Concede on grounding the demo in real stats. Push back:
you're conflating "isolated mechanism evidence" with "end-to-end win." We physically cannot
produce the end-to-end win under the cap. The honest deliverable is: (a) the invariant-enforcing
code, (b) a mechanism demo grounded in real spreads, (c) a documented live-run blocker. That's
not set dressing, that's scoping.

**SRE → SMR (disagree on completeness).** SMR, even granting all your variance math — same-
scenario grouping does NOTHING for a scenario whose rollouts all score identically. Those
degenerate groups produce all-zero advantages. The flat baseline could be partly THAT, not the
mixing. Your fix is necessary-not-sufficient; the code must SURFACE degenerate groups so nobody
thinks this single change rescues a flat run.

## Round 3 — synthesis

- The fix is correct and low-risk **as an invariant enforcer**, regardless of HUD's internal
  grouping (RLE's challenge accepted → claim downgraded from "fixes baseline" to "guarantees
  same-scenario groups + removes between-scenario advantage variance").
- "Variance reduction" will be made **numeric** via the total-variance decomposition, and the
  demo will be **grounded in the real ~0.5/~0.17 reward stats** (REV + DVO).
- The module/demo must **surface degenerate (zero-spread) groups** so the fix isn't oversold
  as a complete cure for flatness (SRE).
- Live GRPO is **out of cap / infra-gated** → ship runnable driver + deterministic demo +
  documented blocker (DVO).
