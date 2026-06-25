# J7 — 04 Spec

## Artifact
`experiments/ralph_outputs/J7/artifacts/agent_bench_runner.py` (stdlib + `requests` via
`agent.llm`). Imports the repo's `agent.llm` (the frozen policy) read-only.

## Data structures

### Registry scenario (existing, read-only) — `{gcp,linode}-bench/scenarios/registry.json`
```
{ incident, service, primary_metric, metric_query, direction, slo_threshold,
  alert_rule, alert_check, cre_id, log_marker, fault_kind, fault_yaml,
  fault_duration_s, fix, fix_timeout_s, skip?, skip_reason? }
```
`fix` is the gold runbook action (a kubectl command string). `skip=true` is excluded.

### Result (emitted)
```
{ bench, mode, model, n, n_actions, correct, action_select_accuracy,
  cloud_executed: false,
  rows: [ { scenario, service, gold_action_index, chosen_action_index, correct,
            request_assembled, raw, chosen_action_cmd, cloud_applied: false,
            cloud_blocked_reason } ] }
```

## Function signatures
- `load_registry(bench:str) -> list[dict]` — non-skipped scenarios for `gcp|linode`.
- `load_cre_text(bench, cre_id) -> str` — raw CRE yaml text (best-effort).
- `build_action_space(scenarios) -> list[str]` — deduped, ordered union of gold fixes.
- `build_prompt(scenario, cre_text, actions) -> str` — SRE incident + numbered menu.
- `_cre_excerpt(cre_text) -> str` — pulls description+mitigation bullets (regex, ≤300 ch).
- `baseline_policy(prompt, scenario, actions) -> int` — deterministic lexical-overlap pick.
- `llm_policy(prompt, model) -> (int, str)` — real `agent.llm.call`; parses first integer.
- `prove_request_assembles(model, prompt) -> bool` — offline `build_request` check.
- `run(bench, mode, model) -> dict` — full result.
- `main() -> int` — CLI.

## CLI contract
```
--bench {gcp,linode}        default gcp
--dry-run                   offline, no API, no cost (default if no --live-agent)
--live-agent MODEL          real LLM (roster name, e.g. claude-haiku-4-5, minimax-m3)
--out PATH                  write result json
```
Mode resolves to `live-agent` iff `--live-agent` is passed, else `dry-run`.

## Reward / scoring rule
`correct = (chosen_action_index == gold_action_index)`.
`action_select_accuracy = correct / n`. Chance ≈ 1/15 = 0.067.
This is **not** the bench's recovery reward and is labeled as such.

## Test cases (`test_agent_bench_runner.py`, offline)
1. both registries load exactly 15 non-skipped scenarios.
2. action space deduped; every gold fix is selectable.
3. prompt contains the service name and all action indices `0..n-1`.
4. `build_request` assembles offline (no network) for every scenario.
5. dry-run `run()` is deterministic (run twice → equal), `cloud_executed is False`,
   accuracy in [0,1], every row `cloud_applied is False`.

## Invariants / safety
- No `gcloud`/`kubectl`/cloud SDK call anywhere in the runner.
- `live-agent` calls the LLM only; it never executes the chosen command.
- Reads registries/CRE files read-only; writes only under `artifacts/`.
