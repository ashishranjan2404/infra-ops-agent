# 04 — Technical Spec

## Inputs / environment
- Scenario id: `cloudflare_waf_regex`
  (spec `scenarios/cidg/generated/76-cloudflare-waf-regex.yaml`, `seed: 1076`).
- Proposer model: `J5_PROPOSER_MODEL` env, default `gpt-5.5` (HUD gateway).
- Judge: `REX_JUDGE_MODE` env, default `deterministic` (no LLM, keyword-set).
- Keys: loaded from `.env` / `~/.zshrc` (`HUD_API_KEY` for the gateway).

## Scenario semantics (from the spec + registry)
- Topology: `edge-proxy → ingress-gw`, `origin-api → ingress-gw`,
  `ingress-gw → waf-engine` (required edges).
- Root cause: `waf-engine`, kind `bad_revision` → category `bad_deploy`, hidden.
- Loud victims (SLO breached): `edge-proxy`, `origin-api` (error_rate_pct > 5).
- Trap action: `scale_deployment(edge-proxy)` — treats `saturation`, a forbidden
  category → blocked by `is_safe` Layer-1.
- Canonical fix: `rollback_deployment(waf-engine)`.

## Runner contract — `artifacts/run_case_study.py`
```
SCENARIO        : "cloudflare_waf_regex"
PROPOSER_MODEL  : env J5_PROPOSER_MODEL  (default "gpt-5.5")
OUT             : artifacts/trace.json

_live_run() -> dict
    load_scenario(SCENARIO)
    proposer(sc, prior_feedback) = rex.loop.propose(sc, prior_feedback, model=PROPOSER_MODEL)
    res = rex.loop.refine_loop(sc, budget=6, propose_fn=proposer, log=collect)
    -> {mode:"live-llm", model, scenario, prompt, result, steps}

_deterministic_trace() -> dict     # fallback if the LLM is unreachable
    run trap_plan (scale edge-proxy) and fix_plan (rollback waf-engine) through run_plan()
    -> {mode:"deterministic-sim-fallback", trap{...}, fix{...}}

main(): try _live_run(); on Exception -> _deterministic_trace() with live_error set.
        Always writes OUT, always prints mode + summary.
```

## Trace record shape (one element of `steps`, from `rex.loop.refine_loop`)
```json
{
  "iter": 0,
  "score": 0.3,
  "resolved": false,
  "stated_root_cause": "<agent's diagnosis sentence>",
  "diagnosis_correct": true,
  "failed_checks": ["correct_fix_missing", "not_resolved"],
  "blocked": [ {"action": {...}, "reason": "..."} ],
  "plan": {"root_cause": "...", "actions": [ {"tool":"...","args":{...}} ]},
  "feedback": "ROOT CAUSE: ... FIX: ... RESULT: ..."
}
```
`result` adds: `outcome` (`resolved`|`escalated`), `clean_win`, `best_iter`,
`best_score`.

## `artifacts/trap_vs_fix.json` shape
```json
{ "trap_plan": {...}, "trap_result": {"resolved": false, "blocked_actions":[...]},
  "fix_plan":  {...}, "fix_result":  {"resolved": true,  "root_cleared": true} }
```

## Test cases
- **T1** scenario loads; `fault_node == "waf-engine"`, `category == "bad_deploy"`.
- **T2** trap (`scale_deployment(edge-proxy)`) → `resolved == False` AND appears in
  `blocked_actions` with a `saturation`/forbidden reason.
- **T3** fix (`rollback_deployment(waf-engine)`) → `resolved == True`,
  `root_cleared == True`.
- **T4** live loop produces ≥1 step with `diagnosis_correct == True` and a final
  `outcome` of `resolved` or `escalated` (never crash).
- **T5** artifacts are valid JSON; runner exits 0.

## Deliverable
`CASE_STUDY.md` — narrative grounded ONLY in `trace.json` + `trap_vs_fix.json`,
with verbatim agent strings, the trap counterfactual, and a scoped N=1 disclaimer.
