# SREGym Run Plan — our agent as a non-interactive planner entry

This is the exact procedure a human WITH a cluster would follow. It is NOT executed in
this session (see RUN_PLAN_blocker.md). No fabricated scores anywhere.

## 0. Prereqs (per github.com/SREGym/SREGym)
- Python >= 3.12, Docker, Helm >= 4.0, kubectl, uv, kind.
- `git clone --recurse-submodules https://github.com/SREGym/SREGym`
- `cd SREGym && uv sync && uv run prek install`
- Cluster: `bash kind/setup_kind_cluster.sh x86`  (or arm), OR the Ansible self-managed path.

## 1. Bind the adapter to SREGym's agent API (the integration seam)
SREGym selects an agent by `--agent <name>`. Register a new agent whose body is our
adapter. Concretely, in SREGym's agent registry create `agents/planner_rex.py`:

```python
# planner_rex.py — wraps experiments/ralph_outputs/G1/artifacts/sregym_adapter.py
from sregym_adapter import (SREGymPlannerAdapter, default_propose)

class RexPlannerAgent(SREGymBaseAgent):           # SREGymBaseAgent = SREGym's base class
    def solve(self, problem):
        gatherer = SregymMCPGatherer(problem)      # implements .gather(): MCP metrics/logs/traces
        resolver = SregymKubectlResolver(problem)  # implements .resolve(): kubectl get deploy/sts/node -A
        client   = SregymSubmitClient(problem)     # implements submit_diagnosis/run_command/signal_done
        adapter  = SREGymPlannerAdapter(
            propose_fn=default_propose(model=self.model),
            gatherer=gatherer, resolver=resolver)
        return adapter.run_problem(problem.id, client=client, dry_run=False)
```
The three `Sregym*` classes are thin glue over SREGym's MCP + submission API — that glue
is the ONE piece that cannot be written without reading SREGym's actual base class
(marked `# TODO(integration)` in sregym_adapter.py).

## 2. Run
```bash
python main.py --agent planner_rex --model anthropic/claude-haiku-4-5
# repeat across the 90 problems x 3 runs as SREGym drives them
```

## 3. Report (paired metrics — never escalation alone; PSRE/grill)
Aggregate the per-problem records into:
- diagnosis_rate, mitigation_rate, e2e_rate           (SREGym oracles O_d / O_m)
- harmful_mitigation_rate   (runs where a fired command worsened state / failed O_m after acting)
- escalation_rate           (plans with empty actions -> we escalated)
- out_of_action_space_count + partial_action_space_count  (action-space gap, reported, not scored 0)
- per-partition splits: ported (34) / similar (43) / new (13)
Compare against the published leaderboard (sregym.com/leaderboard) ONLY with the explicit
caveat that our entry is non-interactive while Claude Code / Stratus / Codex are interactive
MCP tool-users. The interesting hypothesis to test: on the NEW partition (where every
leaderboard agent's E2E collapses), does our escalate-instead-of-hallucinate behavior lower
harmful_mitigation_rate without tanking solve-rate?

## 4. Validity guards baked into the adapter
- The proposer is fed a GATHERED observation bundle, not a leaked spec (no withheld
  structure leaks to our agent).
- Inexpressible tools (modify_network_policy, renew_certificate, clear_cache,
  failover_service) are reported as out-of-action-space — NOT executed as a wrong
  kubectl and NOT silently scored.
