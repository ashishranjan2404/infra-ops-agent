# 04 — Technical Spec

## Module: `artifacts/shadow_runner.py`

### Tool classification (the gate basis)
- `READ_TOOLS = {get_metrics, get_logs, get_events, describe_pod, get_deployment_status,
  get_node_status, query_traces, get_alerts}` — no side effects.
- `CONTROL_TOOLS = {end_incident, escalate_to_human}`.
- `_load_write_tools(repo) -> set[str]`: `tools_registry.json` names minus READ minus
  CONTROL. On failure, a conservative hardcoded write set. **Unknown tools are NOT read**
  (so they are never executed).

### Telemetry sources
- `class TelemetrySource`: `.fetch() -> str`; staticmethod
  `parse_prometheus(text) -> dict[str,float]` (skips `#` comments, regex
  `^(\S+?)\s+([-+0-9.eE]+|NaN|±Inf)$`).
- `FixtureSource(path)` — read recorded snapshot.
- `PrometheusSource(base_url, timeout=3.0)` — `urlopen(base_url+"/metrics")`, GET only.

### Observation
- `@dataclass Observation{ raw_metrics, error_rate, cascade_victims, summary }`.
- `observe(source) -> Observation`: aggregate `app_requests_total{app,status}` into per-app
  5xx fraction; victims = apps with err>0.05 sorted desc; human summary string.

### Shadow execution (executes nothing)
- `@dataclass ShadowAction{ tool, args, classification, executed, note }`.
- `class ShadowExecutor(repo)`: `.classify(tool)->"read"|"write"|"control"|"unknown"`;
  `.shadow_dispatch(plan)->list[ShadowAction]` — every action `executed=False`.
- `class ShadowViolation(RuntimeError)`.
- `assert_no_side_effects(actions)`: raises `ShadowViolation` if any `executed` is True.

### Runner
- `@dataclass ShadowReport{ incident, started_at, observation, stated_root_cause,
  proposed_actions, executed_count, safety_guarantee, blocker }`.
- `run_shadow(incident_name, source, propose_fn, repo=None) -> ShadowReport`:
  observe → propose → classify → `assert_no_side_effects` → report. `executed_count == 0`
  invariant.
- `adapt_rex_propose(repo)`: wraps `rex.loop.build_prompt/parse_plan` + `agent.llm.call`
  (live-LLM path; optional).
- `__main__`: argparse `--prometheus|--fixture` (mutually exclusive, required),
  `--incident`, `--live-llm`; prints `ShadowReport` JSON.

## Test cases (`test_shadow_runner.py`)
1. `test_fixture_parses_and_derives_victims` — payments err>0.9; checkout+gateway victims;
   orders nominal.
2. `test_write_actions_are_never_executed` — a plan with 1 read + 2 writes →
   `executed_count==0`, 2 write actions, all `executed is False`.
3. `test_classification_read_vs_write` — get_logs=read, rollback=write,
   escalate_to_human=control, unknown≠read.
4. `test_assert_no_side_effects_raises_if_executed` — `ShadowViolation` on a forged
   executed action.
5. `test_runner_has_no_execution_imports` — source contains no `subprocess`, no
   `/ctl/fault`, no `/ctl/heal`.
6. `test_nominal_telemetry_proposes_nothing` — clean metrics → no victims, "nominal".

## File formats
- `fixture_metrics.txt`: Prometheus text exposition, exact `mreal/server.py` metric
  names/labels, payments-faulted cascade.
- Report JSON: the `ShadowReport` dataclass via `asdict`.
