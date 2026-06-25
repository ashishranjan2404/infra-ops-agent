# D4 — 10 Feedback for the next task

The highest-leverage move was reusing `rex/harness.py::is_safe` verbatim rather than
re-implementing safety inside a training module — it made training-time and eval-time safety
provably identical and let the unit tests assert against real scenario block reasons, which is
far stronger evidence than a mocked gate. When a task says "X in the loop," the deliverable
that survives review is a *tested reward/decision path* wired to the production component plus
a documented, honest backend blocker — not fabricated curves. Two recurring footguns to front-
load next time: (1) relative-path math for artifacts buried 4 dirs under repo root (test BOTH
the pytest-from-root and standalone-from-/tmp import paths immediately), and (2) any change
that conceptually belongs in a shared core file (`train_rft_v2.py`, `hud_env_v2.py`) must ship
as a reviewed `.patch` with its integration points named — here, the env must surface the
parsed plan + scenario id per rollout, which is the real thing blocking an end-to-end run.
