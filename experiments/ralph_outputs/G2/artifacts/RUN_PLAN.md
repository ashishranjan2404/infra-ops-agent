# RUN PLAN — running Stratus against our benchmark (and the blocker)

> **Status: BLOCKED on running real Stratus.** Everything *up to* invoking Stratus is
> built and verified (adapter + stub proof + tests). Stratus numbers are deferred, not
> fabricated.

## What is real and runnable NOW
```bash
# 1. Smoke-run the SREGym adapter on one of our scenarios (real engine verdict):
python experiments/ralph_outputs/G2/artifacts/sregym_adapter.py \
    --scenario scenarios/cidg/22-leaf-bad-deploy-positive.yaml

# 2. Drive the adapter through an external-style agent loop (proves the contract):
python experiments/ralph_outputs/G2/artifacts/stub_agent.py
#    -> prints solve(resolved=True) + trap(resolved=False) + kubectl fidelity; CONTRACT_OK: True

# 3. Run the test suite:
python -m pytest experiments/ralph_outputs/G2/artifacts/test_adapter.py -q
#    -> 10 passed
```
Stratus is a **drop-in for `stub_agent.py`** at the identical tool contract.

## To run REAL Stratus, three things must be supplied (the blocker)
1. **Stratus source + SREGym harness, vendored.** The driver
   (`clients.stratus.stratus_agent.driver.driver`) and SREGym's 5 MCP servers are
   *external* — not present in this repo. Clone SREGym + Stratus and place them so the
   `agents.yaml` `kickoff_command` resolves.
2. **A server that speaks SREGym's MCP tool protocol over our sim.** `sregym_adapter.py`
   implements the tool *semantics* in-process; to feed Stratus it must be wrapped behind
   the same MCP/HTTP endpoint Stratus connects to (`--server http://localhost:8000`).
   This is a thin transport shim: expose `get_metrics / get_logs / get_traces /
   cluster_control / submit_diagnosis / submit_mitigation` as MCP tools backed by a
   `SREGymEnv` instance per problem. (Deliberately NOT built here — it would be an
   unverifiable network server in a sandbox; the in-process class is the verified core.)
3. **An LLM backend + key for Stratus** (Claude Sonnet/Opus 4.x or Kimi-k2.5).
   No live K8s cluster is needed *because* the adapter substitutes the sim — that is the
   whole point of the reverse comparison; but the MCP transport from #2 is required.

## Exact sequence once unblocked
```bash
# (a) stand up the adapter as an MCP server over our scenario set
python -m g2_adapter_server --port 8000 --scenarios scenarios/cidg/generated/*.yaml   # shim from #2
# (b) register agents (this file's agents.yaml) and launch SREGym for Stratus
python main.py --agent stratus --tasklist tasklist.yaml     # SREGym entrypoint
# (c) collect per-scenario diagnosis_correct + mitigation.resolved + untranslated_rate
# (d) report pass@1 by scenario family + the fidelity (untranslated_kubectl_rate)
```

## Scoping the eventual claim (do not over-claim)
- Report Stratus pass@1 **separately** for 1:1-faithful leaf scenarios vs cascade
  scenarios, alongside `untranslated_kubectl_rate`. A high untranslated rate on a
  scenario means that result is interface-bound and must be caveated, not headlined.
- Compare against our agent's pass@1 on the **same** scenarios (from `rex.eval_pass_at_k`).

## Known limitations carried by the adapter (also in 09_critique)
- Only `error_rate_pct` + `p99_latency_ms` are exposed (engine's two metrics). Scenarios
  whose SLOs reference other metrics (e.g. `pod_restarts`, `cpu_utilization_pct`,
  `latency_p99_ms`) raise `KeyError` in `is_resolved` and are **excluded** from the
  runnable set until the engine populates those metrics. The error-rate-only leaf
  scenarios (e.g. `22-leaf-bad-deploy-positive`) are the verified runnable subset.
- Traces are an edge-list approximation flagged `low_fidelity: true`, not Jaeger.
- Diagnosis grading is a deterministic node+kind-keyword check standing in for the real
  LLM judge (kept dep-free).
