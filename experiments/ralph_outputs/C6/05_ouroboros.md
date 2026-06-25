# C6 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — "the reproducibility hawk"
**Problems found:**
1. The driver fixes `seed=0` for the Thompson bandit but the proposers are reasoning
   models that **ignore temperature** — so `propose_ruleset` output varies run-to-run.
   A second run could yield different `best_train_score`/rules. The spec must SAY the
   numbers are a single realized sample, not an expectation.
2. `node_scores` trajectory is recorded but the *tree structure* (which parent each
   node refined) is dropped, so we can't tell if a model improved monotonically or got
   lucky on the seed node. Minor — keep node_scores, acknowledge limitation.

**Fixes applied:** result dict already stores `node_scores[]`; 03/08/09 explicitly
label results as a single-seed case study and discuss non-determinism. Tree topology
omission documented as a known limitation in 09 (not worth re-plumbing under cap).

## Engineer B — "the safety semanticist"
**Problems found:**
1. Comparing `best by TRAIN` rule-sets across proposers conflates two things: proposer
   *quality* and proposer *luck* in the bandit. A proposer that emits one great rule
   early can beat a proposer that emits the same rule late, purely from budget. True —
   but this is the same search every proposer runs, so it's a fair common substrate.
2. Held-out false-allow is the headline, but the **identity** of the false-allow
   matters: a FA on `treats_forbidden_category` (the spanning hazard, IN train) is a
   real generalization failure; a FA on `last_ready_node`/`leak_restart` (single-
   incident hazards, possibly train-only) is out-of-scope per the module's own docs.
   The table's bare FA count blurs these.

**Fixes applied:** result dict stores `heldout_false_allow` as
`(incident, tool, target, hazard)` tuples, so 08 can separate in-scope (forbidden-
category) FAs from out-of-scope single-incident FAs. This is the correct reading.

## Engineer C — "the over/under-engineering auditor"
**Problems found:**
1. Driver runs 3 proposers serially; if the cap is hit mid-deepseek, we lose its row.
   Mitigation already present: per-model try/except + per-model JSON written
   immediately, so partial results survive. Good — keep.
2. Slight over-engineering: `false_allow_rate` is reported but for n=3 held-out
   incidents the rate is a noisy ratio. Keep raw counts as primary (per grill); rate is
   secondary. Acceptable.
3. Under-test: nothing asserts `hs.MODEL` is restored. A leaked global could corrupt a
   later in-process run. Added as test T2 in 07.

**Fixes applied:** kept per-model isolation + immediate writes; added the global-restore
assertion to the test plan; demoted `false_allow_rate` to secondary in reporting.

## Final filtered spec (deltas folded into 04)
- Report held-out FA/FB **counts** as primary; separate in-scope (forbidden-category)
  from out-of-scope single-incident hazards using the recorded hazard tuples.
- Label everything single-seed case study; non-determinism + dropped tree topology are
  stated limitations.
- Keep per-model try/except + immediate per-file writes for cap-resilience.
- Add a `hs.MODEL`-restored assertion to the test step.
