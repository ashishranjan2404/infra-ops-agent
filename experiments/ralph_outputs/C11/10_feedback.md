# 10 — Feedback for the next task

Ablating-by-reason-string was the cleanest way to disable a single rule WITHOUT touching
core: the production `is_safe` already returns distinct, stable reason strings per guard,
so a thin wrapper can flip exactly one decision and leave every other guard on the real
code path — no logic duplication, no core edits, and a one-line test guarantees clean
attribution. Two reusable lessons: (1) Always ground "the N rules" empirically first —
a 30-second hazard-coverage count over all scenarios revealed that only 3 of the 5
is_safe guards actually fire and that one rule (forbidden_category) dominates by label
volume, which reframed the whole result. (2) For any SAFETY component, accuracy drop is
the requested-but-insufficient metric — pair it with false-allows-introduced, because the
rules with the smallest accuracy drop (last-ready-node, leak-restart) are the highest
severity. The next ablation/eval task should default to reporting BOTH and consider a
per-scenario-normalized or severity-weighted view rather than raw pooled accuracy.
