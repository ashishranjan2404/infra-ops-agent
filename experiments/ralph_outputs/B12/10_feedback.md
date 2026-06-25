# 10 — Feedback for the next task

The A1/A2 pass@k JSONs already carry `by_condition[<cond>].per_incident_rewards`, so
per-incident analyses need NO episode re-runs — ingest and reduce. Two cheap wins that
generalize: (1) always derive `n` from the reward-list length, never a metadata `seeds`
field, since they can desync; (2) ingest *multiple* model JSONs at once so findings are
cross-model rather than single-model noise — that turned a soft "3 unsolvable incidents"
into a robust both-models signal, and surfaced 41 learnable-but-hard incidents (zero_shot
fails, rex solves) that are the real motivation for the REx tree. The biggest unresolved
risk for any solvability/pass@k work is the small rep count (3–5) plus correlated
conditions: don't attach per-incident CIs you can't defend; instead disclose n and keep
"unsolvable" an operational triage label. A natural next slice is a threshold sweep
(`--threshold-sweep`) to show how the solvable/unsolvable partition moves with the 0.8 cut.
