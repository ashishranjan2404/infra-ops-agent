# G1 — Plan: Run SREGym benchmark with our agent

## Objective
Directly compare our SRE remediation agent against SREGym's 90 published problems
on SREGym's own harness, so we can place our agent on (or beside) the
`sregym.com/leaderboard` rather than only reporting numbers on our in-house
CIDG sim. Deliver: (1) a research brief on SREGym's harness/interface, (2) an
adapter design that maps OUR agent (plan-JSON-over-simulator) onto SREGym's
problem/submission protocol, (3) a runnable adapter scaffold + a clear run plan,
and (4) an honest, documented blocker because SREGym's live environment is not
installed here.

## What SREGym is (grounded, from the paper + repo)
- Paper: "SREGym: A Live Benchmark for AI SRE Agents with High-Fidelity Failure
  Scenarios", arXiv:2605.07161v1; repo: github.com/SREGym/SREGym;
  site: sregym.com (docs / problems / leaderboard).
- A problem is `P = (E, I, F, O)`: a live Kubernetes **system environment** E,
  an **agent interface** I (MCP servers: Prometheus metrics, Loki logs, Jaeger
  traces, kubectl cluster control, plus a submission API), an injected **fault/noise**
  set F, and **oracles** O = (O_d diagnosis, O_m mitigation).
- 90 problems across 3 partitions: ported (34, from AIOpsLab/ITBench),
  similar (43), new (13). 3 runs/problem, 1 attempt/run.
- Protocol per problem: agent observes E via I -> submits a **natural-language
  diagnosis** (triggers O_d) -> performs **mitigation actions** on the live cluster
  -> signals completion (triggers O_m).
- Grading: O_d = checklist LLM-as-judge, 9 binary questions over 3 dimensions
  (fault localization / characterization / failure scope), default threshold 7/9.
  O_m = problem-specific programmatic verifier that the real system recovered.
  E2E = diagnosis AND mitigation succeed on the same run.
- Run/install: `git clone --recurse-submodules`, `uv sync`, `uv run prek install`;
  a cluster via Ansible (self-managed) or `kind/setup_kind_cluster.sh [x86|arm]`;
  Docker, Helm >= 4.0, kubectl, uv, kind. Entry point:
  `python main.py --agent <name> --model <litellm-string>`. Agents run in
  **isolated Docker containers** and cannot see problem definitions or grading.

## Our agent (what we have to map FROM)
- `rex.harness.load_scenario` -> `Scenario`; `rex.loop.build_prompt/parse_plan`;
  `rex.harness.run_plan` executes a plan against `sim/engine.py`; `rex.scoring`
  is a deterministic judge. `rex.tree.rex_tree` is the REx refinement policy.
- Our agent's OUTPUT is a single JSON object:
  `{"root_cause": "<one sentence>", "actions": [{"tool": ..., "args": {"target": ...}}]}`.
  It does NOT call MCP/kubectl; it does NOT loop against a live cluster; its action
  space is a fixed set of simulator tools (restart_pod, increase_memory_limit,
  scale_deployment, rollback_deployment, modify_network_policy, ...).

## Approach
1. Brief SREGym's interface (above) precisely enough to build against.
2. Design the **adapter**: an `SREGymAgent` shim that SREGym would invoke, which
   internally drives our proposer, translates our plan into (a) a natural-language
   diagnosis string for O_d and (b) a sequence of kubectl/MCP control calls for
   the mitigation phase. Define the tool-name -> kubectl/MCP translation table.
3. Build a runnable scaffold: `sregym_adapter.py` (offline-importable, no cluster
   needed to syntax/contract-check) implementing the diagnosis-string builder and
   the action->command translator, plus a dry-run CLI; a `run_plan.md`; a
   `requirements/setup` note; and a `tests/` self-check.
4. Document the blocker: no live K8s/Docker/MCP stack here, and a deeper semantic
   gap (single-shot plan vs interactive cluster control). Do NOT fabricate scores.

## Files to create (all task-namespaced, no shared-core edits)
- `experiments/ralph_outputs/G1/01..10_*.md`, `SUMMARY.md`, `result.json`
- `experiments/ralph_outputs/G1/artifacts/sregym_adapter.py` — the shim + translator
- `experiments/ralph_outputs/G1/artifacts/action_translation.json` — tool->kubectl map
- `experiments/ralph_outputs/G1/artifacts/test_sregym_adapter.py` — pytest self-check
- `experiments/ralph_outputs/G1/artifacts/run_plan.md` — exact steps to run on a cluster
- `experiments/ralph_outputs/G1/artifacts/RUN_PLAN_blocker.md` — the documented blocker

## Dependencies / risks
- SREGym requires a live K8s cluster + Docker + Helm + MCP servers — NOT installed.
- Semantic mismatch: our agent is single-shot plan emission; SREGym expects an
  interactive observe->diagnose->mitigate loop with arbitrary kubectl. The adapter
  can bridge the I/O contract but cannot, without real cluster access, prove the
  mitigation oracle passes. This is the honest ceiling of this task.
- Action-space gap: some SREGym faults (TiDB/MongoDB/Kafka, OS/hardware faults)
  have no corresponding tool in our 12-tool simulator action space -> those
  problems are out-of-distribution for our agent and must be reported as such,
  not silently scored 0 or faked.

## Success criteria
- A precise, citable interface brief.
- An adapter that imports cleanly, translates every one of our tools to a concrete
  kubectl/MCP command, builds a valid diagnosis string from a plan, and passes its
  own pytest in dry-run mode.
- A run plan a human with a cluster could literally follow.
- A blocker section that is specific (what's missing, what would unblock it) and
  contains ZERO fabricated benchmark numbers.
