# E3 — 10 Feedback for the next task

The OpenSRE forked slugs (`opensre-qwen3-8b-1e439a`, and `opensre-qwen3-30b`) and the base
`Qwen/Qwen3-8B` are all **live and 200-reachable on the HUD inference gateway** — you can score them
with the ordinary `agent.llm.call` path by registering the slug into a *local* roster copy
(`ROSTER.setdefault`), so there's no need for the `.venv-hud` Tinker SDK just to *evaluate* a trained
model (training still needs Tinker; inference does not). Reuse `rex.harness` + `rex.scoring` (the P0
deterministic judge) + `experiments.compute_pass_at_k` rather than rebuilding eval — it gives
reproducible, LLM-judge-free numbers in ~1s/episode. Two real blockers to carry forward: (1) the
**Fireball arm is empty** — E2 and D8 produced no dataset/model, so any Fireball comparison is
blocked until that pipeline ships; do not fabricate it. (2) The OpenSRE-vs-zero-shot lift is **small
and CI-overlapping** (pass@1 0.107 vs 0.071), matching the known flat-training result — if the next
task wants a non-null, train on the harder cascades with more steps (per the rft-training-run memo)
and/or evaluate the 30B fork, and consider a `<think>`-aware plan parser since the reasoning-model
output currently caps measurable reward for both arms symmetrically.
