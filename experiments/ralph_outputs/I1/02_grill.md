# 02 — Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DOL** DevOps Lead.

## Round 1 — initial takes

**SMR:** A "graduation framework" is only interesting if it's a *statistical* claim about a
policy over a distribution, not a property of one rollout. Define earned-autonomy as a
hypothesis test: clean-win rate on held-out solvable incidents exceeds a threshold with a
confidence bound. Anything per-episode is reward-noise.

**PSRE:** From an on-call standpoint, "earning autonomy" = blast radius. I don't care that a
bot can diagnose; I care which *actions* it's allowed to take unsupervised. Read-only
forever-fine; `restart` after some evidence; `scale` and destructive ops only after a lot.
And the killer criterion is **correct escalation** — a junior who knows when to page me is
worth more than one who always acts. The project already says 0.86 ceiling = solve-4 +
escalate-1. Build the tiers on that.

**AAAI:** For this to be publishable rather than hand-wavy, you need (1) precise predicates,
(2) a soundness argument that graduating implies a bounded harm rate, and (3) revocation, or
reviewers will say "monotonic trust is unsafe." Also: what's the population? If you graduate
on the same incidents you tuned on, it's contaminated. Demand a held-out distribution.

**RLE:** Reuse what exists. `rex/loop.py` already computes `clean_win` and `outcome ∈
{resolved, escalated}` and `failed_checks` already enumerates `trap_action`. Don't invent a
new scorer — the graduation predicate should be a pure function of batches of those records.
Keep it executable so it's testable.

**DOL:** Whatever you define has to map to an enforcement point: an RBAC/guardrail tier the
agent is *granted*. Graduation should literally toggle which tools the harness `is_safe` lets
through. And revocation has to be automatic and fast — one harmful action and we yank perms,
no human in the loop for the demotion.

## Round 2 — react to another persona BY NAME (forced disagreement)

**PSRE → SMR (disagree):** SMR's "just clean-win rate with a confidence bound" is *unsafe* as
the sole criterion. A policy can have a 95% clean-win rate and still occasionally `scale` a
crash-looping control plane and herd its datastore — that's a SEV1. Clean-win rate is an
*average*; a trap is a *tail*. Graduation must be conjunctive: high clean-win **AND a hard
zero-trap requirement** on the eval window, not a rate that averages traps away.

**SMR → PSRE (concede partly, push back):** Fair on the tail — I'll make trap-rate a hard
gate, not a soft term. But PSRE's pure-blast-radius view under-specifies *evidence*. "Allowed
to restart after some evidence" — how much? Without a sample-size / confidence device you
graduate on 3 lucky rollouts. So: tiers from PSRE, but each tier gates on a **Wilson lower
bound** of clean-win, so small n can't graduate.

**AAAI → RLE (disagree):** RLE says "reuse `clean_win`, it's already a pure function of the
records." But `clean_win` in `loop.py` is `∃ iteration with no failed_checks` — that's
**existential over the refinement budget**. For an autonomy claim that's generous: it means
"somewhere in 6 tries it was clean." A reviewer will object that earned autonomy should be
about the *committed* plan (the one actually executed), not the best of 6. You must define the
graduation statistic on the FINAL/best committed outcome, and be explicit that REx's internal
search is allowed but the *graded* event is the committed action.

**RLE → AAAI (defend, then adjust):** The committed outcome IS the best-scoring iteration —
REx commits its best candidate, and the safety gate `is_safe` filters every proposed action
*before* apply, so the "best of 6" still never executed a blocked action. But AAAI's point
stands for *traps that the gate doesn't catch*: I'll define the graduation event on the
committed plan's `failed_checks`, and separately count any trap **proposed and not blocked**
as a hard fail, since that's the thing that would actually fire in production.

**DOL → AAAI (disagree on revocation latency):** AAAI wants a clean monotone proof; I want
revocation that fires on a *single* incident. Those conflict: a statistical graduation bar
(needs n samples) but a 1-event revocation. I'm fine with the asymmetry — *graduation is
slow and evidence-heavy, revocation is instant*. That asymmetry is the safety property, not a
bug. Encode it.

**SMR → DOL (disagree on enforcement coupling):** DOL wants graduation to literally toggle
RBAC. That couples the *measurement* to the *enforcement* and makes the framework un-testable
offline. Keep them separate: the framework outputs a *tier grant* (data); a downstream
controller may enforce it. The formalization should be enforcement-agnostic.

## Round 3 — synthesis (what we agree on)

1. **Tiers = blast radius** (PSRE, DOL): ordered T0 read-only ⊂ T1 restart ⊂ T2 scale ⊂ T3
   destructive. Higher tier ⇒ stricter evidence bar.
2. **Per-tier graduation statistic is conjunctive** (PSRE, SMR): (a) Wilson lower bound of
   clean-win rate on held-out *solvable* incidents ≥ θ_T, AND (b) correct-escalation rate on
   held-out *unsolvable* incidents ≥ ε_T, AND (c) **hard zero** proposed-and-unblocked trap
   actions on the eval window. Escalation is a first-class win (AAAI/PSRE, grounded in the
   0.86 ceiling).
3. **Graduation event = committed plan**, not best-of-budget, and any unblocked trap is a
   hard fail (AAAI, RLE).
4. **Held-out distribution required** (AAAI) — graduate on scenarios disjoint from any tuning
   set.
5. **Revocation is instant and asymmetric** (DOL): one unblocked trap, OR a sliding-window
   clean-win / escalation rate below a floor, demotes immediately.
6. **Measurement is enforcement-agnostic** (SMR): output a tier grant; enforcement is
   downstream. Reuse `failed_checks` / `outcome` semantics verbatim (RLE).
