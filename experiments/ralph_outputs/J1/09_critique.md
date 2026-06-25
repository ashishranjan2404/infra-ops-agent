# J1 — 09 Critique (honest)

## The headline weakness
The task says "deploy the agent in a staging K8s cluster with real chaos injection."
The single most important word is **real**, and the one thing I could not do is touch a
real cluster. gcloud auth is dead (`Account has been deleted`) AND the API server times
out (private/firewalled endpoint). So the central, hardest claim — that the agent
survives genuine infra faults — is **unproven**. Everything I shipped is correct
scaffolding plus an offline twin; a skeptic is right to say "you didn't actually do the
hard part." I agree. I chose not to switch to the other gcloud accounts because they're
not the cluster's project account, switching is global state that could disrupt other
concurrent Ralph workers, and the API server is unreachable anyway so it wouldn't help.

## What a reviewer attacks next
- **"The sim backend just re-encodes the topology you already know."** True — `_sim_observe`
  is a faithful but circular twin: it can't surprise you the way a real cascade can
  (LB masking, scrape gaps, partial pod death, timing). Its value is validating the
  harness plumbing and grader, not discovering emergent behavior.
- **"The in-cluster Job won't run as written."** Correct — `python:3.11-slim` has no
  `kubectl`, so `--backend kube` inside the Job fails. I flagged this (05/06) and the
  validated path is the local/workstation kube backend. Still, the manifest as shipped
  is aspirational for the in-cluster case.
- **"HTTPChaos may not intercept without per-pod setup."** Real risk on some GKE
  installs; mitigated by documenting the CNI-level fallback ladder, but not proven.
- **"Five hand-written ground-truth labels is a small eval."** Fair. It's a
  representative spread (error/latency/pool/network/availability) but it's not a
  statistically meaningful benchmark; pass@k over many seeds would be the real test.

## What's missing
- An actual `kubectl apply --dry-run=server` against a reachable cluster (the strongest
  offline-ish validation) — impossible here.
- Real Prometheus scrapes to confirm the cascade shape matches `sim/engine.py`'s
  `propagate()` — the transfer claim the ML researcher persona cared about is asserted,
  not measured.
- A kubectl-bearing runner image so the Job is genuinely deployable.

## What's genuinely solid
- The chaos design is grounded in the actual deployed mesh and its control plane, with a
  defensible Chaos-Mesh-vs-Litmus rationale.
- Safety is real and structural (namespace scope, bounded duration, finally-heal,
  least-priv RBAC verified by assertion) — this would not damage the live cluster.
- The grader is the project's own shared judge, executed, not reimplemented — so live
  and offline results are comparable on the same rubric.

## Honest status
Deliverable: complete and validated offline. Live execution: blocked by external
auth+network failure, documented to the byte. Not a fabricated success.
