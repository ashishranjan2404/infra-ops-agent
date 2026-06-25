# F14 — 10 Feedback for the next task

The single highest-leverage move was reconciling the two narrative sources before writing a
word: `ARCHITECTURE.md` is the optimistic pitch (REx lifts every model to 0.86) while
`docs/headline_insights.md` is the honest self-audit (that lift is mostly oracle-feedback
leakage; the defensible core is the env + the *searched* verifier). Any content task in this
repo should treat `headline_insights.md` as the source of truth for what may be *claimed* and
`ARCHITECTURE.md` for system/structure — never present the rosy numbers without the ablation
caveat, or a reviewer-persona will (correctly) tear it apart. Second lesson: build a tiny
machine-checkable invariant even for a "soft" deliverable — the `timing_check.py` validator
caught a real 13:45-vs-claimed-15:00 arithmetic error I'd have otherwise shipped, so any future
outline/budget/doc task should ship with a parser that asserts its own headline claims. Keep
all writes namespaced under the task dir; the two narrative docs are read-only gold and must
not be edited.
