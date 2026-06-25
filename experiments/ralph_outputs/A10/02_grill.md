# A10 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (REV),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial take
- **SMR**: Blast radius is a useful per-incident *difficulty/severity* covariate.
  It lets us stratify eval and weight reward by impact. Just don't let it leak the
  answer to the policy at solve-time — keep it a sidecar for analysis, not an input.
- **PSRE**: Blast radius in real SRE = downstream services that breach SLO because
  of the root cause. The topology edges already encode "required" dependencies, so
  graph reachability is the right primitive. But "affected" must follow dependency
  direction correctly — a DB fault hits its *callers*, not its dependencies.
- **REV**: A count alone is not a contribution. You need a *defined* propagation
  model and a validation that it matches the scenario's own `assertions.cascades`
  and `slo` node list. Otherwise it's an arbitrary number.
- **RLE**: I want this as a column I can join on incident id for curriculum
  ordering and pass@k slicing. CSV + JSON both, stable ids.
- **DOL**: Map tiers to SEV1/2/3 the way an on-call would read them. A 1-service
  contained blip is not SEV1 even if severity float is high.

## Round 2 — react to another persona (genuine disagreement)
- **PSRE → SMR**: I disagree that it's "just analysis". Blast radius IS the label
  many of these scenarios already imply via the `slo` block — those list the nodes
  expected to breach. If my reachability set disagrees with the SLO node set, one of
  them is wrong. We should cross-check, not treat blast radius as free-floating.
- **REV → DOL**: Your SEV mapping is hand-wavy. "1 service = not SEV1" ignores that
  a single auth service down can be a company-wide SEV1. Tiering purely on count is
  naive; you must combine count *and* root severity *and* cascade assertion.
- **RLE → REV**: Disagree that a count "isn't a contribution". For RL curriculum the
  count is exactly the actionable signal — I don't need a publishable model, I need a
  monotonic difficulty proxy. Over-formalizing this wastes the budget.
- **SMR → PSRE**: Cross-checking against `slo` nodes is appealing but the SLO block
  only lists *monitored* nodes, not all *affected* nodes — they're different sets.
  Forcing them to match would corrupt the metric. Report both; don't assert equality.
- **DOL → REV**: Fair — I'll fold root severity and cascade into the tier, not count
  alone. But a SEV1 needs a multi-service OR a high-sev-cascade condition, else every
  big topology auto-becomes SEV1 and the tier loses signal.

## Round 3 — synthesis
- Propagation = **reverse reachability** over `required` edges from the root cause
  (faults flow to callers). Validate direction on a hand-checked scenario.
- Tier = function of (#affected, root severity, cascade assertion) — not count alone
  (REV+DOL accepted). SEV1 if >=4 affected or (sev>=0.9 and cascade).
- Treat blast radius as a **sidecar covariate** for eval/curriculum (SMR+RLE), and
  *report* the SLO-node set alongside but DO NOT force equality (SMR rebuttal accepted).
- Keep it small and runnable (RLE); add one validation + unit tests (REV) so the
  number is defined and reproducible, not arbitrary.
