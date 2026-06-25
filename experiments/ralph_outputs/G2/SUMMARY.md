# G2 — Summary: Run our benchmark with SREGym's Stratus agent (reverse comparison)

## Outcome: COMPLETED deliverable, Stratus run BLOCKED (no fabrication)

Built infrastructure to run an external SREGym agent (Stratus) against our CIDG
benchmark, proved it with a stub agent, and documented why a real Stratus run is blocked
- without fabricating any Stratus numbers.

## Deliverables (task-namespaced; no shared-core edits)
- artifacts/STRATUS_BRIEF.md  - Stratus design brief, sourced from arXiv 2506.02009 /
  2605.07161 + sregym.com: multi-agent state machine (detection/diagnosis/mitigation
  sub-agents); Transactional No-Regression (TNR) safety spec; observes & acts only via
  5 MCP servers (Prometheus/Loki/Jaeger/kubectl/Submission) over a live K8s cluster;
  Claude 4.x + Kimi-k2.5 backends.
- artifacts/sregym_adapter.py - SREGymEnv: exposes our sim/engine.py scenarios through
  those 5 tool families, incl. best-effort kubectl -> 25-verb-registry translation with
  an untranslated_kubectl_rate fidelity counter.
- artifacts/stub_agent.py  - deterministic SREGym-shaped client proving the loop (solve
  resolves, trap fails) -> CONTRACT_OK: True. Stratus is a drop-in.
- artifacts/agents.yaml  - SREGym registration (documented schema) for stratus + cidg-stub.
- artifacts/test_adapter.py  - 10 pytest cases, all pass.
- artifacts/RUN_PLAN.md  - runnable commands today + 3-part blocker + unblock sequence.

## Key real results (measured)
- Adapter runs end-to-end with a genuine sim.engine verdict (rollback->resolved True,
  restart_pod->False).
- 58/61 CIDG scenarios run cleanly and resolve via canonical fix; 3 error because their
  SLOs name metrics the Tier-A engine doesn't populate (pod_restarts/cpu_utilization_pct/
  latency_p99_ms) - a real engine/SLO finding.
- 10/10 tests pass; agents.yaml parses.

## Blocker (why no Stratus score)
Real Stratus needs: (1) its driver + SREGym's 5 MCP servers vendored (external, absent),
(2) an MCP/HTTP transport wrapping the adapter (--server :8000; not built, unverifiable
in sandbox), (3) an LLM key for Stratus. No live cluster needed because the adapter
substitutes the sim. Everything up to invoking Stratus is real and verified.
