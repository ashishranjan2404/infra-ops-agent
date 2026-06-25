# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **Emit a confusion matrix + per-category recall**, not just a scalar
   (accepted SMR/AAAI). Implemented in `evaluate()` -> `confusion`, `per_category_acc`.
2. **Decoupling is now a first-class output.** The run prints the % of records
   where root-cause-correct disagrees with incident-resolved (accepted DOL/RLE).
   Implemented via `_resolved_flag()` + `rc_vs_resolved_disagree`.
3. **Vocab frozen on taxonomy semantics, accuracy reported honestly even if low**
   (accepted AAAI). No tuning loop against the 197-record set.
4. **Hermetic guarantee made explicit**: the metric imports only
   `rex.scoring._stems`; tests use no network/LLM (accepted DOL).

## Critiques accepted
- SMR/AAAI confusion-matrix transparency — accepted.
- DOL decoupling-must-be-shown — accepted (this is the metric's reason to exist).
- AAAI no-test-set-tuning — accepted; vocab is semantic, accuracy left as measured.
- PSRE wrong-mechanism-must-be-wrong — accepted; classification is by *mechanism
  category* (kind), so right-service/wrong-mechanism lands in a different category.

## Critiques rejected (with reason)
- SMR's "use a learned classifier": REJECTED. PSRE's interpretability argument
  wins for an SRE-facing metric, and a learned model adds an opaque dependency and
  its own training data. The keyword matcher's failure modes are visible in the
  confusion matrix, which satisfies SMR's transparency requirement another way.
- AAAI's implied "don't ship if accuracy is low": REJECTED as a blocker. A low but
  HONEST number on real verbose answers is a valid measurement and itself a finding
  (models bury the category under multi-cause narratives).

## Net deliverable
Same as 01 plus: confusion matrix, per-category recall, and an on-real-data
decoupling statistic — all hermetic.
