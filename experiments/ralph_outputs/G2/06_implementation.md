# G2 — Implementation

## What I built (all under `experiments/ralph_outputs/G2/artifacts/`, no shared-core edits)

1. **`sregym_adapter.py`** — `SREGymEnv`, a SREGym-shaped environment over our CIDG sim.
   Exposes all 5 SREGym tool families backed by `sim.engine`:
   - `get_metrics` (Prometheus stand-in) — `World.metric` for `error_rate_pct` /
     `p99_latency_ms` over all nodes.
   - `get_logs` (Loki stand-in) — `observation.smoking_guns` signatures buried under noise.
   - `get_traces` (Jaeger stand-in) — edge-list approximation, flagged `low_fidelity`.
   - `cluster_control` (kubectl stand-in) — accepts BOTH a structured `{tool,args}` call
     and a free-form `kubectl ...` string, which it best-effort translates to our 25-verb
     registry. READ verbs (`get/describe/logs/top`) are observation no-ops; unmappable
     mutations are counted toward the `untranslated_kubectl_rate` fidelity metric.
   - `submit_diagnosis` / `submit_mitigation` (Submission stand-in) — NL diagnosis graded
     by node+kind-keyword; mitigation verdict from `sim.engine.is_resolved`.
   - `fidelity()` — kubectl call count + untranslated count + rate.

2. **`stub_agent.py`** — deterministic SREGym-shaped client (NOT Stratus). Drives the
   adapter through the full loop and runs a **solve** episode (canonical fix -> resolved)
   and a **trap** episode (wrong tool -> not resolved), plus a kubectl-passthrough demo.
   Proves the verdict is real + falsifiable. Prints `CONTRACT_OK: True`.

3. **`agents.yaml`** — SREGym registration (documented schema) for `stratus` (upstream
   driver command) + our `cidg-stub`. Parses with `yaml.safe_load`.

4. **`test_adapter.py`** — 10 pytest cases covering reset, metrics, structured fix,
   wrong-tool, kubectl translation, kubectl read no-op, untranslated counting, diagnosis
   positive/negative, traces flag.

5. **`STRATUS_BRIEF.md`** — Stratus agent-design brief from the papers (multi-agent state
   machine, TNR safety spec, 5 MCP servers, LLM backends), with the integration-surface
   analysis driving the adapter and the fidelity-scoping for any eventual comparison.

6. **`RUN_PLAN.md`** — exact runnable commands today + the precise 3-part blocker to run
   real Stratus + the unblock sequence + carried limitations.

## Empirical result of building it (real, measured)
- Adapter runs end-to-end on a real scenario: rollback on `checkout-api` ->
  `is_resolved == True`; `restart_pod` -> `False`. (Verified, see 07.)
- Across the full scenario set: **58/61 scenarios run cleanly through the adapter and all
  58 resolve via their canonical fix**; **3 scenarios error** because their SLOs reference
  metrics the Tier-A engine does not populate (`latency_p99_ms`, `cpu_utilization_pct`,
  `pod_restarts`). Those 3 are excluded from the runnable set and documented — this is a
  REAL finding about the engine/SLO surface, not a fabrication.

## A note on the would-be shared-core change
A faithful run would benefit from the Tier-A engine populating the extra SLO metrics
(`pod_restarts`, `cpu_utilization_pct`, `latency_p99_ms` alias). Per the parallel-safety
rule I did **not** edit `sim/engine.py`. The adapter instead handles the gap by excluding
those scenarios and counting them; the proposed engine extension is left as a noted
follow-up (a one-metric-alias + a derived `cpu_utilization_pct`), not applied.

## What I did NOT do (honest scope)
- Did NOT run Stratus (source/MCP bundle external, no transport server — see blocker).
- Did NOT build the live MCP/HTTP transport server (would be an unverifiable network
  service in this sandbox); the in-process `SREGymEnv` is the verified core and the
  transport is a documented thin wrapper.
