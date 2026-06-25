# G2 — Feedback for the next task

The reverse-comparison tasks (run an external agent on our benchmark) are gated by one
recurring fact: external SRE agents (Stratus, and likely Claude-Code-as-SRE, Codex)
couple to their benchmark ONLY through SREGym's 5 MCP tool families against a LIVE
Kubernetes cluster with free-form `kubectl` + Prometheus/Loki/Jaeger — whereas our world
is a Python sim with two metrics and a closed 25-verb registry. So every such task should
plan for an adapter that (a) exposes our sim as those 5 tool families and (b) *measures*
the interface gap (`untranslated_kubectl_rate`) rather than hiding it; the honest blocker
is always "no vendored agent source + no MCP transport server + no LLM key," which is a
finite, nameable checklist, not a vague 'can't run it.' Two concrete carry-overs: (1) our
Tier-A engine only populates `error_rate_pct`/`p99_latency_ms`, so 3 hand-authored
scenarios crash `is_resolved` on `pod_restarts`/`cpu_utilization_pct`/`latency_p99_ms` —
worth a follow-up to populate/alias those metrics (a real shared-core change to propose,
not sneak in); and (2) `scenarios/cidg/22-leaf-bad-deploy-positive.yaml` is the
reliable error-rate-only smoke scenario (rollback resolves, restart_pod doesn't) — use it
as the canonical proof fixture for any adapter that needs a clean, fully-supported episode.
