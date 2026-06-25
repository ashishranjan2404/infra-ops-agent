# D6 — 10 Feedback for next task

The repo's HUD trajectory dumps (opensre-traj/out/hud_trajectories.jsonl) are a
goldmine of reward-ranked completions and double as preference data for free — any
task needing chosen/rejected pairs, ranking, or judge signal should start there rather
than generating new rollouts. Two reusable lessons: (1) the deterministic judge in
rex/scoring.py is the canonical reward and should be the single source of truth for
both signal generation and eval, named explicitly in configs to preempt leakage
critiques; (2) for any training task in this env, the binding constraint is the same —
only forked OPEN models (Qwen via HUD) are trainable and there's no local GPU/torch,
so ship a validated dependency-free dry-run plus an actionable backend blocker instead
of attempting (and faking) a real run. One gap worth fixing upstream: the trajectory
exporter doesn't store the realized prompt, forcing approximate reconstruction from
templated specs — a future task could add prompt logging to make all downstream
preference/SFT data exact.
