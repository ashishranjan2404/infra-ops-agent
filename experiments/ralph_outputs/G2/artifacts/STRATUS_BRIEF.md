# Brief: SREGym's Stratus agent (for the G2 reverse comparison)

> Sourced from the Stratus paper (arXiv 2506.02009), the SREGym paper
> (arXiv 2605.07161 / ACM AIAgentic 2025), and SREGym docs (sregym.com/docs).
> **Stratus was NOT executed in this task** — see RUN_PLAN.md for the blocker.

## What Stratus is
**STRATUS** — "A Multi-agent System for Autonomous Reliability Engineering of Modern
Clouds." It is the reference state-of-the-art SRE agent shipped/benchmarked with SREGym,
and is reported to beat prior SRE agents by >=1.5x on AIOpsLab and ITBench.

## Architecture (as described)
- **Multi-agent state machine.** Specialized sub-agents for *failure detection*,
  *diagnosis*, and *mitigation*, coordinated as a state machine that also carries the
  safety reasoning. This is the key contrast with our single-proposer REx loop.
- **Safety spec — Transactional No-Regression (TNR).** A formal property the state
  machine enforces: a remediation step must not regress system health vs. before it ran;
  the design enables "safe exploration and iteration" (try, check no-regression, keep or
  revert). This is conceptually adjacent to our trap-action / harness gating, but Stratus
  enforces it *transactionally at runtime against the live cluster*, not against a
  closed action vocabulary.
- **LLM backends.** Evaluated with Claude Sonnet/Opus 4.x and Kimi-k2.5 (per SREGym).

## How it observes & acts (the integration surface that matters for G2)
SREGym makes **no assumption** about an agent's internal architecture; it couples agents
only through tools. Stratus, like any SREGym agent, perceives & acts via **5 MCP servers**
SREGym stands up against a **live Kubernetes cluster**:
1. **Metrics** — Prometheus time-series.
2. **Logs** — Loki.
3. **Traces** — Jaeger.
4. **Cluster control** — arbitrary **`kubectl`** (observe + mutate live K8s objects).
5. **Submission** — submit the NL **diagnosis** (root-cause localization) and trigger
   **mitigation** evaluation.

Problems have up to two graded phases: **diagnosis** (localize + explain the root cause
in natural language) and **mitigation** (actually restore the cluster). SREGym launches
the agent as an external process via `agents.yaml` (`kickoff_command`), e.g. the Stratus
driver connects to a server:
`python -m clients.stratus.stratus_agent.driver.driver --server http://localhost:8000`.

## Why this matters for running Stratus on OUR benchmark
Our CIDG benchmark is a **simulator**, not a live cluster:
- We expose a Python API (`World`, `apply_action`, `is_resolved`) and a **closed
  25-tool registry**, not free-form `kubectl` over real K8s objects.
- Metrics are *functions* of a hidden fault + topology (two metrics:
  `error_rate_pct`, `p99_latency_ms`), not dozens of Prometheus series.
- There is no Loki/Jaeger; our "logs" are buried smoking-gun signatures and our "traces"
  are an edge-list approximation.

So Stratus cannot be pointed at our benchmark as-is. The G2 adapter
(`sregym_adapter.py`) bridges this by presenting our sim through Stratus's exact 5 tool
families, including a **best-effort `kubectl` -> 25-verb translation** with an
`untranslated_kubectl_rate` fidelity counter (so the interface gap is measured, not
hidden).

## Fidelity ceiling / scope of any eventual comparison (be honest)
- **Faithful** on 1:1-mapped *leaf* scenarios (e.g. bad-deploy -> `rollout undo`):
  a Stratus pass/fail there is a genuine reasoning signal.
- **Lossy** on cascade-heavy scenarios where Stratus would emit rich `kubectl get -o yaml`
  / Prometheus queries our two-metric world can't answer; report
  `untranslated_kubectl_rate` as the fidelity metric and scope the claim accordingly.
- **TNR vs our verdict:** Stratus's transactional no-regression check expects a live
  cluster it can probe between steps; our `is_resolved` is a single end-of-episode
  ground-truth predicate. A faithful run should let Stratus re-read `get_metrics` after
  each `cluster_control` (the adapter supports this), approximating TNR.
