# 10 — Feedback for the next task

The biggest unblock this task: **Anthropic credits are exhausted on this machine,
so any path through the default `rex/loop.py` proposer (`claude-haiku-4-5`) or the
`rex/scoring.py` LLM judge will 400.** Do not treat that as a hard blocker — the
HUD inference gateway works: `gpt-5.5` and `gemini-3.1-pro` are reachable (export
`HUD_API_KEY` via `set -a; source ~/.zshrc; set +a`; `deepseek-v4-pro` returned
empty, avoid it). Route any frozen LLM call to the gateway by passing a custom
`propose_fn=lambda sc,fb: propose(sc,fb,model="gpt-5.5")` into `refine_loop`, and
keep `REX_JUDGE_MODE=deterministic` (the default) so the judge needs no LLM at all —
this lets you run the *real* loop without editing a single core file. The generated
scenarios in `scenarios/cidg/generated/` are loadable by their **registry key**
(e.g. `cloudflare_waf_regex`, underscores), not their filename; check
`registry.json` (32 entries) for the exact keys. Finally, the loop stops early on a
clean win, so don't assume `budget` iterations ran — read `best_iter`/`len(steps)`.
A wrong-tool-then-corrected trace (like iter-0 `failover_service` → iter-1
`rollback_deployment` here) is the strongest signal your output is REAL, not staged.
