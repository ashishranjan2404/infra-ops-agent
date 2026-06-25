# G2 — Plan: Run OUR benchmark with SREGym's Stratus agent (reverse comparison)

## Objective
The "forward" comparison (G1) runs *our* agent on *their* 90 SREGym problems.
G2 is the **reverse**: run *their* state-of-the-art agent (**Stratus**) against
*our* CIDG benchmark (the ~33 hand-authored + ~51 generated scenarios driven by
`sim/engine.py`). If Stratus does well on our scenarios, our benchmark is "easy /
already-solved"; if it stumbles on the cascades/traps our engine emits, that is direct
evidence our benchmark adds signal a frontier SRE agent misses.

## What Stratus actually expects (researched, not assumed)
Stratus is the reference agent shipped with **SREGym** (arXiv 2506.02009 / 2605.07161).
Key facts established from the papers + SREGym docs:
- SREGym does **not** call an agent in-process. It launches the agent as an external
  process via `agents.yaml` (`kickoff_command`, `kickoff_workdir`, `kickoff_env`). The
  shipped Stratus entry is:
  `python -m clients.stratus.stratus_agent.driver.driver --server http://localhost:8000`
- The agent observes/acts **only** through 5 MCP servers SREGym stands up against a
  **live Kubernetes cluster**:
  1. Metrics — Prometheus time-series
  2. Logs — Loki
  3. Traces — Jaeger
  4. Cluster control — arbitrary `kubectl`
  5. Submission — `submit_diagnosis` (NL root cause) and `submit_mitigation`
- Problems have up to two phases: **diagnosis** (NL root cause) and **mitigation**
  (restore the cluster). Stratus is a multi-agent **state machine** with a safety
  spec (Transactional No-Regression, TNR); LLM backends include Claude Sonnet/Opus 4.x
  and Kimi-k2.5.

## The core mismatch (this drives the whole task)
Our scenarios are **not** a live K8s cluster. `sim/engine.py` exposes a *Python* API:
`World(spec)`, `apply_action(world, Action(tool,args))`, `is_resolved(world)`, plus
typed metrics (`error_rate_pct`, `p99_latency_ms`) over a dependency graph. Our action
space is a **closed 25-tool registry** (`tools_registry.json`), NOT `kubectl`. There is
no Prometheus/Loki/Jaeger; metrics are *functions* of the hidden fault + topology.

So Stratus cannot be pointed at our benchmark "as-is". A faithful reverse comparison
needs a **shim** that makes our sim *look like* a SREGym environment to Stratus:
expose our metrics as MCP-Metrics, our smoking-gun logs as MCP-Logs, our 25 tools as
MCP cluster-control verbs, and our `is_resolved`/diagnosis-judge as MCP-Submission.

## Approach (scaffold + run plan + honest blocker)
1. **Brief** Stratus's design from the papers (06/artifacts/STRATUS_BRIEF.md).
2. **Adapter scaffold** (`sregym_adapter.py`): a SREGym-shaped **environment server**
   over our sim — a small JSON-RPC / HTTP tool server exposing exactly the 5 SREGym
   tool families, backed by `sim.engine.World`. This is the piece that would let
   *any* SREGym-registered agent (incl. Stratus) drive our scenarios.
3. **`agents.yaml` + run plan**: the SREGym registration we *would* use for Stratus,
   plus the exact commands to wire it, and what we cannot run and why.
4. **Self-test** the adapter end-to-end with a tiny **stub agent** (a deterministic
   policy) so the adapter is proven to actually run an external agent loop against our
   scenarios — Stratus is then a drop-in for the stub at the same interface.
5. **Document the blocker**: Stratus source is not vendored here, there is no live
   GKE/LKE cluster wired for this run, and SREGym's MCP server bundle is external. We
   deliver the runnable adapter + the precise wiring, not fabricated Stratus scores.

## Files to create (all task-namespaced — NO shared-core edits)
- `experiments/ralph_outputs/G2/artifacts/sregym_adapter.py` — the env-as-tool-server.
- `experiments/ralph_outputs/G2/artifacts/stub_agent.py` — deterministic external agent
  proving the loop (Stratus-shaped client).
- `experiments/ralph_outputs/G2/artifacts/agents.yaml` — SREGym registration for Stratus
  + our stub.
- `experiments/ralph_outputs/G2/artifacts/STRATUS_BRIEF.md` — agent-design brief.
- `experiments/ralph_outputs/G2/artifacts/RUN_PLAN.md` — exact steps to run Stratus once
  the blocker is cleared.
- `experiments/ralph_outputs/G2/artifacts/test_adapter.py` — self-test.

## Dependencies
- `sim/engine.py`, `sim/spec.py`, `tools_registry.json`, `scenarios/cidg/**` (read-only).
- Stdlib only for the adapter (no new pip deps) so the scaffold runs in this env.

## Risks
- Over-fitting the adapter to *our* tool names (Stratus emits `kubectl`, not
  `scale_deployment`). Mitigation: the cluster-control tool accepts BOTH a structured
  `{tool,args}` call and a best-effort `kubectl`->our-tool translation table, and we
  document the translation as a known fidelity gap.
- The diagnosis phase is NL; grading needs our judge. We reuse the deterministic
  diagnosis check rather than an LLM judge to keep the scaffold dep-free.

## Success criteria
- Adapter imports + runs a full episode (reset -> observe -> act -> submit -> evaluate)
  against a real CIDG scenario via the stub agent, returning a real resolved/diagnosis
  verdict from `sim.engine`.
- `agents.yaml` is valid and matches SREGym's documented schema.
- Blocker is specific and reproducible (what's missing, what would unblock it).
- No shared-core file modified.
