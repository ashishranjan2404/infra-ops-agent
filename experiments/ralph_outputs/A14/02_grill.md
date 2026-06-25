# A14 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **REV** AAAI Reviewer ·
**RLE** RL Engineer · **DEV** DevOps Lead.

## Round 1 — initial take
- **SMR**: Good idea — a flat iteration budget is an unrealistic cost model. But "time =
  sum of proposer latencies" couples the metric to hardware/network jitter. For a
  *reproducible* eval you want a deterministic surrogate (token count, or a fixed per-call
  cost), with real wall-clock only for live demos.
- **PSRE**: From on-call reality the binding constraint is rarely "seconds" — it's **number
  of risky actions** and **MTTR against an SLA**. I want a *step budget* (actions) as the
  primary axis and time as secondary. Also: a budget cutoff should map to **escalation**, not
  silent failure — that's literally what an SRE does when the clock runs out.
- **REV**: Where is the *evidence* this changes rankings? A budget knob with no demonstrated
  effect on outcomes is a parameter, not a contribution. Show at least one scenario where the
  budget flips win→escalate. Also define the cost model precisely or it's unfalsifiable.
- **RLE**: For RL this is reward shaping under a constraint. The clean design is a
  *constrained episode*: terminate when budget hits 0, reward = best in-budget score. Don't
  re-define reward; just truncate the rollout. Keep it a wrapper so the env stays frozen.
- **DEV**: Please do NOT touch `rex/*.py`. Many workers run in parallel. A config + wrapper is
  the only safe move. Ship named presets so eval sweeps are one-liners.

## Round 2 — react to another persona BY NAME (genuine disagreement)
- **PSRE → SMR**: I disagree that time should be secondary-only. SMR wants determinism, fine,
  but *eval realism* needs the time axis as a first-class citizen — a model that needs 9 slow
  calls IS worse on-call than one that needs 2. Keep BOTH axes; make time deterministic via an
  injectable `cost_fn`, don't demote it.
- **SMR → REV**: REV's "show a flip" demand is right and I'll meet it, but REV's implied bar
  ("prove it changes frontier rankings") is too high for a *harness* task. The deliverable is
  the instrument; the ranking study is a downstream eval run. Don't conflate building the
  thermometer with taking the temperature.
- **REV → RLE**: RLE says "don't re-define reward, just truncate." But truncation silently
  changes the *outcome distribution* — escalations now include budget-induced ones. That must
  be **labeled** (`budget_truncated`, `truncation_reason`), or downstream analysis can't tell a
  genuine escalation from a clock-out. I push back on "just truncate."
- **RLE → PSRE**: PSRE wants step-budget primary. Disagree — a single expensive action and a
  cheap one cost the same step, which understates risk. But I'll concede steps are the *cleaner*
  deterministic axis, so keep both and let the config pick.
- **DEV → REV**: REV wants a precise cost model; agreed, but don't gold-plate it into a
  full token-accounting system. A pluggable `cost_fn` (default = real latency, override = fixed)
  is precise *enough* and keeps the wrapper small.

## Round 3 — synthesis
Consensus design:
1. **Two budget axes**, both optional, config-selected: `time_budget_s` and `step_budget`.
2. **Determinism via injection**: `cost_fn(t0,t1)->seconds` and a `clock` callable, so tests
   and demos are reproducible offline; default = real wall-clock for live runs. (SMR+PSRE+DEV)
3. **Constrained-episode semantics**: truncate the rollout at the last in-budget iteration;
   reward = best in-budget score; budget cutoff ⇒ `escalated`. (RLE+PSRE)
4. **Label everything**: `budget_truncated`, `truncation_reason`, full per-iter meter, so a
   budget-induced escalation is distinguishable from a genuine one. (REV)
5. **Demonstrate a flip**: ship a demo where a slow 2-try model wins under loose budgets and
   escalates under `pager-storm`. (REV)
6. **Wrapper only, named presets.** (DEV)
