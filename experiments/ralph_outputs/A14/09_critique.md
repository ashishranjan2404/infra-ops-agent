# A14 — 09 Critique (honest)

## What a reviewer will attack
1. **"You built the thermometer but didn't take the temperature."** The strongest criticism.
   I deliver the budget-limited *variant harness* and an offline demo of a win→escalate flip,
   but NOT a live frontier sweep showing how real models' pass@k degrades under `tight` /
   `pager-storm`. That study needs API access (HUD_API_KEY / gateway models) and is a separate
   eval job. The contribution here is the instrument + a deterministic proof it bites; the
   ranking impact is asserted, not measured.
2. **Uniform step cost is a weak risk model.** A `restart_pod` and a `drain_node` cost one step
   each, yet the second is far riskier. Real on-call "budget" is partly a *risk* budget. v2:
   generalize `cost_fn` to `action_cost_fn(action)->float` keyed on tool danger. Left out to
   avoid over-engineering v1.
3. **Time = sum of proposer latencies ignores sim/judge/tool-exec time.** Defensible (the model
   call dominates), but a purist will note the wall-clock model is incomplete. The injectable
   `cost_fn` lets a user define any cost surrogate, so this is configurable rather than wrong.
4. **Soft-ceiling-at-boundary is a footgun.** `time_budget_s=5` with `5s/call` buys exactly ONE
   call, not "everything that fits in 5s". Documented and tested, but a careless user may set
   the budget one call too tight. A stricter "would this call exceed?" pre-check is an
   alternative; I chose "finish the action you started" as the more SRE-realistic rule.
5. **Demo uses a synthetic canned proposer.** The flip is real *given* a 2-try model, but the
   "2-try" behavior is scripted, not emergent from a real model. With a live model the same
   wrapper would produce the analogous (un-scripted) effect — untested here.

## What's genuinely solid
- Zero core edits; enforced purely through the loop's public `propose_fn` / `log=` / `budget=`.
- Fully deterministic, offline, fast tests (7/7) using the REAL loop + sim + judge.
- Truncation is *labeled*, so budget-induced escalations are analytically separable from
  genuine "no safe fix" escalations — directly addressing the AAAI reviewer's R2 critique.

## Honest status
Deliverable COMPLETE (real plan + spec + runnable wrapper + passing offline tests + demo with a
measured flip). The one downstream piece — a live budgeted model sweep — is BLOCKED on API
access and explicitly scoped out, not faked.
