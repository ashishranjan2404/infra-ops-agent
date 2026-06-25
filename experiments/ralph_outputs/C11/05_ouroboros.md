# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — Correctness auditor
**Problems found:**
- A1. `_state_for` sets `mem_leak_active = (sc.kind == "mem_leak")` unconditionally, but
  `build_state` ANDs in `"increase_memory_limit" not in applied_tools`. For the labeled
  examples there is no applied-tools history (single-action decisions), so the two agree —
  but this MUST be documented or a reader thinks it diverges from production state.
- A2. `predict_block` validated `disabled` only when `is_safe` blocked (early-return on
  allow skipped the check) → an unknown rule id could silently no-op on allowed actions.
**Fix:** A1 documented inline. A2 fixed: validate `disabled in RULES` at the top of
`predict_block` before any short-circuit.

## Engineer B — Safety / metrics reviewer
**Problems found:**
- B1. Accuracy on an imbalanced set hides the safety story. A rule could have ~0 accuracy
  drop yet remove a catastrophic false-allow.
- B2. "First match wins" means R1 can mask R2/R3 on the same action, under-crediting them.
**Fix:** B1 — every row reports `false_allows_introduced`; the table prints a `+FA` column.
B2 — documented as a known property in the module docstring and 03/08; we report
marginal-given-others deliberately (it answers "what does deleting this rule cost").

## Engineer C — Scope / reproducibility reviewer
**Problems found:**
- C1. If one scenario fails to load, a crash loses the whole run.
- C2. R4_replica_limit may show 0.0 drop and read as "dead rule," an over-claim.
- C3. Import must work regardless of cwd (Ralph workers run from varied dirs).
**Fix:** C1 — per-scenario try/except collects `scenarios_skipped` with the error, run
continues. C2 — R4 kept and flagged in 06/09 as "untriggered in this scenario set," not
"useless." C3 — script inserts repo root on `sys.path` from its own location.

## Final filtered spec (deltas applied)
- `predict_block` raises `KeyError` for an unknown rule up-front (A2).
- Per-scenario load is fault-tolerant; skips recorded (C1).
- mem_leak_active equivalence to build_state documented inline (A1).
- `+FA` / `-FB` columns + JSON fields are first-class (B1).
- Masking caveat + R4-untriggered framing documented (B2, C2).
- cwd-independent imports (C3).
All four points landed in `rule_ablation.py` / `test_rule_ablation.py` as shipped.
