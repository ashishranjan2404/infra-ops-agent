# E5 — Feedback for the next task

When a task names a specific model/checkpoint ("Fireball") that may not exist in the
repo, check `agent.models.ROSTER` and probe reachability FIRST — it determines whether
you're delivering a result or a scaffold-plus-blocker, and shapes the whole plan. Reusing
a prior task's curated artifact (A8's held-out manifest) is a huge win: it gives a
provenance-stamped, novelty-guarded set for free and keeps tasks consistent — always
look for an upstream deliverable before deriving your own. Bake controls in as gates, not
afterthoughts: an `empty` floor (must be 0) and an `oracle` ceiling (must be 1) doubled
as a *data-validity* check that caught nothing here only because the incidents were sound
— but they'd have flagged an unsolvable incident instantly. Finally, distinguish three
failure modes explicitly in any multi-policy harness — *blocked* (no provider),
*reachable-but-empty* (low score, real), and *fabricated* (never) — because conflating
them is exactly how fake numbers sneak in; record the error string and keep going so one
dead policy never kills the live baseline.
