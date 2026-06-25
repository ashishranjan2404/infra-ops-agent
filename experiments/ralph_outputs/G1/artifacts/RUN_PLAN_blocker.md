# BLOCKER — why G1 cannot produce real SREGym scores in this environment

## Hard blocker (infrastructure): SREGym's live environment is not installed
SREGym is a LIVE benchmark. Each problem is a running Kubernetes deployment with injected
faults, queried through MCP servers (Prometheus/Loki/Jaeger) and mutated via kubectl, with
agents sandboxed in isolated Docker containers. Running it requires, on this machine, all of:
- the SREGym repo cloned with submodules (NOT vendored in /Users/mei/rl),
- a Kubernetes cluster (kind or Ansible self-managed) — none running here,
- Docker daemon + Helm >= 4.0 + kubectl + uv + Python >= 3.12 SREGym env,
- the MCP observability stack + fault injectors deployed into that cluster.
None of this is present. Standing it up is a multi-hour, multi-GB, arch-sensitive
(x86 vs arm) operation. Therefore NO score was produced and none is fabricated.

## Soft blocker (integration seam): SREGym's submission API names are not public
The public paper/repo excerpt does not publish the exact Python class/function names of
the diagnosis/mitigation submission API. The adapter targets a minimal `SREGymClient`
Protocol (`submit_diagnosis` / `run_command` / `signal_done`) and the `--agent` base-class
registration seam. Three glue classes (`SregymMCPGatherer`, `SregymKubectlResolver`,
`SregymSubmitClient`) must be written against SREGym's real `BaseAgent` at install time —
flagged `# TODO(integration)` in code and in run_plan.md.

## Semantic blocker (deeper, would persist even WITH a cluster): two real gaps
1. **Interaction model.** Our agent is a non-interactive PLANNER (one plan JSON). SREGym
   reference agents (Claude Code, Stratus, Codex) are interactive MCP tool-users that loop
   observe->act->observe. Any leaderboard comparison is therefore a transfer/zero-shot
   result, explicitly labeled — not like-for-like. (Mitigated, not removed, by feeding our
   proposer a gathered observation bundle so it doesn't get a leaked spec.)
2. **Action-space gap.** Our fixed 12-tool vocabulary cannot express several SREGym
   mitigations: `modify_network_policy`, `renew_certificate`, `clear_cache`,
   `failover_service` have no faithful generic kubectl mapping (the real fix is a
   problem-specific NetworkPolicy / Secret / cache endpoint / Service selector). And
   SREGym spans TiDB/MongoDB/Kafka/OS/hardware faults entirely outside our K8s-workload
   tools. Those problems are tagged out-of-action-space and reported as N/A — never faked,
   never silently scored 0.

## What would unblock it
- Provision a kind cluster + install SREGym (run_plan.md step 0) — unblocks infra.
- Read SREGym's `BaseAgent`/submission API and implement the three `Sregym*` glue classes
  — unblocks the integration seam.
- Accept the non-interactive caveat OR wrap our plan policy in a multi-turn tool-using
  loop (a separate, larger task) — addresses the semantic gap.
The adapter, translation table, tests, and run plan in this directory are the real,
validated deliverable that makes those steps mechanical.
