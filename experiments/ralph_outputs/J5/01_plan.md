# 01 — Plan (J5: incident case study, end-to-end)

## Objective
Produce a **narrative case study** of one real incident run end-to-end through the
SRE-Degrees agent: the incident, the agent's step-by-step reasoning, the trap it
avoided, the fix, and the outcome. Use **REAL agent output** if the loop is
runnable; otherwise trace the deterministic sim.

## Scenario choice
`cloudflare_waf_regex` — the **Cloudflare 2019-07-02 WAF regex CPU exhaustion**
outage (`scenarios/cidg/generated/76-cloudflare-waf-regex.yaml`), already wired
into the registry as a loadable `rex.harness` scenario (family: `novel`,
style: `cascade`). It is an ideal case study because:
- **Real, famous outage** (a backtracking regex in a new WAF rule pinned CPU
  across Cloudflare's edge, global 502s).
- **Loud-alert-≠-root cascade**: the loudest CPU/503 signal is on `edge-proxy`,
  but the root is upstream on the shared `waf-engine`.
- **Clear trap**: `scale_deployment(edge-proxy)` — chasing the loud alert; the
  harness blocks it because it treats a ruled-out `saturation` cause.
- **Clear fix**: `rollback_deployment(waf-engine)` — roll back the bad rule.

## Approach
1. Load the scenario via `rex.harness.load_scenario`.
2. Run the **real linear refine loop** `rex.loop.refine_loop` (frozen proposer LLM
   + deterministic judge + Tier-A sim) for budget 6.
3. Capture the full per-iteration trace (root cause, actions, blocked actions,
   failed checks, feedback) to a JSON artifact.
4. Separately demonstrate the **trap path** vs the **fix path** through the sim.
5. Write the narrative case study from the captured real output.

## Files to create (all task-namespaced — NO core edits)
- `experiments/ralph_outputs/J5/artifacts/run_case_study.py` — runner
- `experiments/ralph_outputs/J5/artifacts/trace.json` — real loop trace
- `experiments/ralph_outputs/J5/artifacts/trap_vs_fix.json` — sim demonstration
- `experiments/ralph_outputs/J5/CASE_STUDY.md` — the narrative deliverable
- `01..10` step files + `SUMMARY.md` + `result.json`

## Dependencies
`rex/{harness,loop,scoring,escalate}.py`, `sim/engine.py`, `agent/{llm,models}.py`,
a reachable frozen LLM. Read-only imports of all of these.

## Risks
- **Anthropic credits exhausted** (known machine state) → the default haiku
  proposer 400s. Mitigation: route the proposer to a reachable HUD-gateway model
  (gpt-5.5) via `propose(..., model=)`; keep a deterministic-sim fallback so a
  real artifact is produced regardless.
- LLM nondeterminism → the trace is one real run; the deterministic sim + judge
  make the *grading* reproducible even if the proposer's wording varies.

## Success criteria
- A real captured agent trace showing diagnosis, the avoided trap, the fix, and a
  resolved outcome (or an honest blocked outcome).
- A coherent narrative case study grounded in that captured output.
- No shared core file modified; all artifacts validate/run.
