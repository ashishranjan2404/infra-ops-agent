# 06 — Implementation

## Artifacts built (all under `experiments/ralph_outputs/J2/artifacts/`)
1. **`shadow_runner.py`** (~270 lines) — the shadow-mode harness.
   - `READ_TOOLS` / `CONTROL_TOOLS` constants + `_load_write_tools(repo)` reading the real
     `tools_registry.json` (24 tools; 8 read, 2 control, 14 write).
   - `TelemetrySource` (+ `parse_prometheus`), `FixtureSource`, `PrometheusSource` —
     `/metrics` GET only.
   - `observe()` → `Observation` (per-app 5xx error rate + ranked cascade victims).
   - `ShadowExecutor.classify/shadow_dispatch` — labels actions, executes **nothing**;
     `ShadowViolation`; `assert_no_side_effects`.
   - `run_shadow()` → `ShadowReport` with `executed_count` (invariant 0) + a stated
     `safety_guarantee` string.
   - `adapt_rex_propose()` — optional live-LLM proposer reusing `rex.loop.build_prompt/
     parse_plan` (read-only import of shared core; not modified).
   - `__main__` CLI: `--prometheus | --fixture`, `--incident`, `--live-llm`.
2. **`fixture_metrics.txt`** — recorded-real Prometheus snapshot of a payments-faulted
   CIDG mesh (exact `mreal/server.py` metric shape). payments=98% 5xx (root),
   checkout/gateway loud downstream victims, orders/db nominal.
3. **`test_shadow_runner.py`** — 6 pytest cases proving the guarantee + parsing.

## The safety guarantee (how it is enforced)
- **Structural:** the module imports neither `sim.engine.apply_action` nor `subprocess`,
  and contains no `/ctl/fault|heal` POST. There is *no code path* that mutates live state.
- **By data:** every `ShadowAction.executed` is set `False`; `run_shadow` calls
  `assert_no_side_effects`, which raises `ShadowViolation` if `executed_count != 0`.
- **By test:** `test_runner_has_no_execution_imports` greps the source for forbidden
  execution primitives; `test_write_actions_are_never_executed` asserts `executed_count==0`
  on a plan containing real write tools.

## Grounding in existing code
- Reasoning side reused unchanged from `rex/loop.py` (frozen-model proposer, JSON plan
  parse) via `adapt_rex_propose`.
- Telemetry shape mirrors `mreal/server.py::_metrics()` (the live GKE call-mesh).
- Read/write tool split mirrors `rex/loop.py::_remediation_tools()` and the registry.

## Shared core files modified
**None.** All new files are task-namespaced. The live-LLM path imports `rex.loop` and
`agent.llm` read-only.

## Proposed-but-not-applied change (documented, not made)
A production deployment would add `mode="shadow"` to `rex/harness.py::run_plan` so the
*same* loop can run shadow or live. We did **not** edit `rex/harness.py` (shared core).
Sketch of the intended guard, for review only:
```python
def run_plan(plan, scenario, settle_ticks=5, mode="live"):
    if mode == "shadow":
        # classify-only; never call apply_action
        return shadow_dispatch_report(plan, scenario)
    ...  # existing live path
```
This belongs in a follow-up PR against the core file, not in this worker.
