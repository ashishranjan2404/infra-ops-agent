# 01 — Plan (J2: shadow-mode live-incident runner)

## Objective
Run the SRE agent against a LIVE incident in **shadow mode**: observe real telemetry,
propose (never execute) remediation, log the diagnosis. Deliver the shadow harness +
a *provable* safety guarantee that no action is executed, plus an honest write-up of the
live-incident-access blocker.

## Approach
- Reuse the existing frozen-model proposer (`rex/loop.py: propose/parse_plan/build_prompt`)
  unchanged — shadow mode changes the *execution* side, not the *reasoning* side.
- Telemetry comes from the live CIDG call-mesh (`mreal/server.py` exposes Prometheus
  `/metrics`; a fault at one node cascades to callers — gateway is the loud victim).
- The safety guarantee is **structural, not policy**: the shadow runner does NOT import
  `sim.engine.apply_action`, does NOT shell out to `kubectl`, and does NOT POST to the
  mreal `/ctl/fault|heal` control plane. It can only *classify* actions (read vs write
  via `tools_registry.json`) and record what *would* happen. `assert_no_side_effects`
  is a runtime check that `executed_count == 0`.
- Pluggable telemetry: `PrometheusSource` (live) and `FixtureSource` (recorded snapshot)
  so the harness + safety path are byte-identical offline (no cluster) and online.

## Files to create (all task-namespaced)
- `artifacts/shadow_runner.py` — the harness.
- `artifacts/fixture_metrics.txt` — recorded faulted-mesh `/metrics` snapshot.
- `artifacts/test_shadow_runner.py` — pytest proving the guarantee.

## Files NOT to modify
`rex/*.py`, `sim/*.py`, `agent/*.py`, `mreal/*`, `experiments/*.py`. The runner imports
`rex.loop` read-only for the live-LLM path only.

## Dependencies / risks
- Live incident needs a running GKE cluster + Prometheus + an injected fault — **not
  available to this worker** (see 07/09). Mitigated by the fixture path.
- Live-LLM proposer needs an API key/credits — also a blocker; mitigated by an offline
  stub proposer so the harness + safety path are fully exercised.

## Success criteria
1. Runner observes real Prometheus text, derives the cascade (root vs downstream victims).
2. Agent proposes a plan; every write action is recorded as `executed: false`.
3. `executed_count == 0` always; a test asserts a `ShadowViolation` if that's ever false.
4. No execution imports (`apply_action`, `subprocess`, `/ctl/...`) anywhere in the module.
5. End-to-end CLI run on the fixture prints a real ShadowReport.
