# B14 — Improved Plan (post-grill)

## What changed vs 01_plan
1. **Per-row `price_assumed` flag** (accepted, AAAI). Every output row carries whether its price
   is a real published number (Claude) or a documented assumption (gateway/fireworks slug). The
   price table is dumped into `cost_efficiency.json` with `assumed` + `note` per model.
2. **Judge cost = $0, but explicit and overridable** (accepted, RLE/AAAI). `JUDGE_CALLS=0`
   reflects the deterministic P0 scorer actually used; a comment + a unit test pin this, and the
   LLM-judge path (max_tokens=8) is documented so flipping it is a one-line change.
3. **Output-token utilization is a single named parameter** (accepted, DVO). Default 0.6, stated
   in the table header. Noted that the cross-condition ranking within a model is invariant to it
   (it scales uniformly); only cross-model absolute $ moves.
4. **Report `$/100-incidents` and `cost x vs zero_shot`** (accepted, DVO/SMR) — the ops-budget and
   reviewer-facing columns, alongside the raw ratio.
5. **Framing caveat** (accepted, PSRE): the metric is documented as a *secondary efficiency axis*,
   NOT a training objective — captured in `09_critique.md`. For high-severity incidents, MTTR
   (task A9) dominates; $/pass can mislead. This is a usage caveat, not a code change.

## What I rejected and why
- **PSRE: "don't ship a cost metric, it's dangerous as a signal."** Rejected as stated. A correct
  secondary metric isn't dangerous; *misusing* it as the sole objective is. I keep the metric and
  add the usage caveat instead of dropping it. (SMR's rebuttal stands.)
- **"Estimate is garbage-in" (AAAI, strong form).** Rejected the conclusion. Tokens aren't logged
  — that's a fact of the existing artifacts, not a choice. The brief explicitly allows documented
  assumptions when counts aren't logged. The mitigation is transparency (flags + overridable
  constants + derivation from real code), which I implemented, not abandoning the deliverable.

## Final shape (unchanged from plan, hardened)
- `cost_model.py` (prices + call shape + estimator) — unit-tested.
- `cost_per_dollar.py` — ingests A1/A2 real pass@1 JSONs, emits table (md + json).
- Generated: `cost_efficiency.json`, `cost_efficiency_table.md`.
