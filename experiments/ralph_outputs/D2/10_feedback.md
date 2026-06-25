# D2 — 10 Feedback for the next task

Preflight the backend before designing the run — a single `hud models list` turned this from
"train Qwen-14B" into "14B doesn't exist on Tinker; deliver a verified substitute + loud
preflight," which is the honest and far more useful outcome. When a task names a specific
model size, check the gateway's *actual* trainable inventory first (here: Qwen dense rungs are
4B / 8B / 27B — no 14B), because requested sizes are often aspirational. Reuse the proven core
trainer (`train_rft_v2.py`) by *import + delegation* rather than copy-paste; this satisfies
parallel-safety (no core edits) and avoids regressions. And when compute caps forbid the real
run, the strongest deliverable is a runnable launcher whose preflight returns exit 0 against a
*verified-trainable* base — that is reproducible evidence of readiness, and it beats any
fabricated training curve. Next worker: if you pick up the real 27B/30B run, validate the
fork's checkpoint tree before trusting `--reset-head` (the core swallows that failure).
