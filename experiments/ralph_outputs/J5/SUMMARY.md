# J5 — Summary

**Task.** Create a case study: one incident end-to-end with the agent.

**Scenario.** `cloudflare_waf_regex` — the **Cloudflare 2019-07-02 WAF regex CPU
exhaustion** outage (`scenarios/cidg/generated/76-cloudflare-waf-regex.yaml`,
seed 1076). A loud-alert-≠-root cascade: loudest CPU/503 on `edge-proxy`, real
root upstream on `waf-engine`.

**What ran (REAL agent output).** The actual `rex.loop.refine_loop` (frozen
proposer + deterministic judge + Tier-A sim) on the scenario. Proposer routed to
`gpt-5.5` via the HUD gateway because Anthropic credits are exhausted (the default
Haiku 400s). Captured in `artifacts/trace.json`:
- **Iter 0:** correct **upstream** diagnosis (`waf-engine`) *before any feedback*,
  but wrong fix tool (`failover_service`) → not resolved, score 0.3.
- **Iter 1:** kept the diagnosis, switched to `rollback_deployment(waf-engine)` →
  **resolved**, score 1.0, clean win. Total **2 iterations**.

**Trap avoided.** The agent never proposed scaling the loud victim; separately,
`artifacts/trap_vs_fix.json` shows `scale_deployment(edge-proxy)` is blocked by
`is_safe` (forbidden `saturation` category) and never resolves — vs the fix which
resolves and clears the root.

**Deliverable.** `CASE_STUDY.md` — narrative of incident → reasoning → trap → fix
→ outcome, grounded only in the captured JSON, with an N=1 scope statement and an
honest limitations section.

**Artifacts (all task-namespaced, no core edits):**
- `artifacts/run_case_study.py` — runner (live loop + deterministic fallback)
- `artifacts/trace.json` — real live trace
- `artifacts/trap_vs_fix.json` — trap-vs-fix sim demonstration
- `CASE_STUDY.md` — the narrative deliverable
- `01..10` step files

**Tests.** T1–T5 pass; docs parse; runner re-runs and exits 0. See `07`.

**Status:** completed. Blocker (Anthropic credits) worked around via the gateway,
not faked.
