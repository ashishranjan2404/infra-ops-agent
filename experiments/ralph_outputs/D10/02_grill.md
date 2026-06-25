# D10 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **REV** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial takes
- **SMR:** A reward sweep is cheap and high-value. But "composite reward changed" is a
  weak claim — what matters for RFT is whether the **advantage ranking within a group**
  changes. Report Kendall tau, not just means.
- **PSRE:** From an ops standpoint the only weighting that's operationally defensible is
  one where *trap actions* (scaling a leaking service, restarting a crash-looping control
  plane) can never out-score a clean fix. The sweep must include a `no_trap_penalty`
  variant to show what breaks if you drop it.
- **REV:** Where do the rollouts come from? If they're LLM samples, the result is not
  reproducible and I'd reject. If they're synthetic, say so plainly and justify that the
  conclusion (reward *re-weighting* behavior) doesn't depend on rollout realism.
- **RLE:** RFT here is GRPO-style. A weight change only matters if it changes the sign or
  ordering of advantages within a scenario group. A uniform shift in all rewards is a
  no-op after baseline subtraction. So measure **argmax flips** and **tau**, and also
  warn when a weighting *compresses* spread (kills trainability).
- **DVO:** Whatever you build, it must not touch `rex/scoring.py`. Other Ralph workers run
  in parallel. Wrapper only, task-namespaced output.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SMR:** I disagree that tau alone is enough. Tau is invariant to *spread*. A
  weighting can keep the exact ranking but squash all rewards into [0.3,0.35] — tau=1.0
  yet GRPO advantages vanish (division by tiny std → noise). You MUST also report spread,
  or you'll bless an untrainable reward.
- **PSRE → REV:** You're too precious about rollout realism. I don't care if the rollouts
  came from a real model — I care that the *trap* candidate exists and gets scored. The
  sim's `run_plan` actually executes the action and tells me if it resolved. That's more
  honest than an LLM transcript I can't reproduce. Synthetic-but-sim-executed is the
  RIGHT call, not a compromise.
- **REV → PSRE:** Pushing back: "the trap exists and gets scored" is necessary but not
  sufficient for a paper. If every scenario yields the *same* ranking (correct_full >
  fix_wrong > ... > trap), then the sweep is a tautology — you designed the candidates to
  rank that way. The result is only interesting if some weighting **reorders** them. Show
  me at least one argmax flip, or the contribution is null.
- **SMR → RLE:** Fair on spread, but note GRPO normalizes per-group; a constant
  TRAP_PENALTY shift is NOT uniform across a group because only trap candidates eat it —
  so it genuinely reshapes advantages. Dropping the penalty should flip argmax on
  scenarios where a trap happens to resolve the SLO. That's the test.
- **DVO → SMR:** Don't over-engineer the grid. Eight hand-chosen weightings that bracket
  the design space beat a 4-D cross product nobody will read.

## Round 3 — synthesis
Consensus deliverable:
1. Rollouts are **synthetic candidate plans executed through the REAL sim** — reproducible,
   no LLM. State this limitation explicitly (REV).
2. Report, per weighting: **mean composite**, **spread** (RLE/SMR), **Kendall tau vs
   default** and **argmax-flip rate** (RLE/REV). Spread guards trainability; tau+flips
   guard "did the optimization target actually move."
3. Must include `no_trap_penalty` and `harsh_trap` (PSRE) and `resolution_only` (the
   degenerate end-case REV wants).
4. The headline must be honest: if rankings barely move, say so. A flip on even a few
   scenarios is the real, defensible finding (REV).
5. Wrapper only; selftest asserts equivalence to `score_plan` at default (DVO).
