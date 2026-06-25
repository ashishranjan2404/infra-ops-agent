# E4 — 10 Feedback for the next task

The repo's REx eval primitives (`load_scenario`, `run_plan`, `build_prompt`,
`parse_plan`, `score_plan` + `compute_pass_at_k`) compose cleanly into a new
task-namespaced harness with **zero** shared-core edits — lean on them rather than
re-deriving scoring. Two reality checks save time up front: (1) before promising
trained-model comparisons, grep for the slug — Fireball and the OpenSRE-GRPO Qwen
are NOT in this repo (corroborated by `experiments/results/P7_fireball_status.md`),
so any "trained-vs-trained" task is checkpoint-blocked and should ship as
harness + honest blocker; (2) of the roster, only the Fireworks models
(`glm-5p2`, `minimax-m3`) reliably return content — Anthropic 400s (credits) and the
gateway reasoning models return empty strings, so default to Fireworks for any
stand-in run and keep both policies on the same provider to avoid the cross-provider
prompt-assembly bias baked into `agent/llm.py`. Finally, when a stand-in produces a
directional "verdict", carry the caveat *in the same JSON object* — a bare
`B_HURTS` string will get quoted out of context otherwise.
