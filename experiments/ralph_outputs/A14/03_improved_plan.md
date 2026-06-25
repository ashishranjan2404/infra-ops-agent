# A14 — 03 Improved Plan (post-grill)

## What changed vs 01_plan
1. **Determinism made first-class.** Added an injectable `cost_fn(t0,t1)->seconds` and a
   `clock` callable. Default = real wall-clock (live runs); tests/demos inject a fixed
   per-call cost so the whole pipeline runs offline and reproducibly.
   *(accepted: SMR's reproducibility critique; PSRE's "keep time first-class".)*
2. **Two axes, both optional, config-selected**: `time_budget_s` AND `step_budget`. A tighter
   preset must not exceed a looser one on either axis (asserted in a test).
   *(accepted: PSRE step-axis + SMR/RLE determinism; rejected PSRE's "step primary, time
   secondary" — kept symmetric.)*
3. **Explicit truncation labels**: `budget_truncated`, `truncation_reason`, and a full
   per-iteration meter in the result. A budget-induced escalation is now distinguishable from
   a genuine "no safe fix exists" escalation.
   *(accepted: REV's "label the outcome distribution" — this was the strongest critique.)*
4. **Constrained-episode semantics, lossless**: truncate at the last in-budget iteration via a
   pre-flight check; keep all completed iterations through the loop's `log=` hook; reward =
   best in-budget score; cutoff ⇒ `outcome="escalated"`.
   *(accepted: RLE's "truncate, don't re-define reward".)*
5. **Demo proves a flip**: a slow 2-try model wins under `unbounded/relaxed/tight` but
   escalates under `pager-storm`. *(accepted: REV's "show evidence".)*

## Critiques rejected (and why)
- **REV: "prove it changes frontier rankings."** Rejected as out of scope: A14 builds the
  *instrument* (budget-limited variant), not the downstream ranking study. The harness is the
  deliverable; running a full frontier sweep under budgets is a separate eval job (and needs an
  API key / live models we treat as a documented follow-up).
- **PSRE: "step budget primary."** Rejected — kept both axes symmetric so config selects the
  realistic constraint per deployment; a step-only model understates the time cost of a slow
  model (RLE's point).

## Final shape
`BudgetConfig(time_budget_s, step_budget, iter_cap, label)` + `PRESETS` +
`run_budgeted_episode(scenario, cfg, base_propose_fn, cost_fn=..., clock=...)` →
loop result dict augmented with a `budget` report and truncation labels. No core edits.
