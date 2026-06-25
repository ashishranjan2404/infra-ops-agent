# J1 — 01 Plan

## Objective
Deploy the SRE/REx agent against a **staging Kubernetes cluster with REAL chaos
injection** (not the scripted `sim/engine.py` cascades). Deliver three things the
task names explicitly:
1. a **deployment manifest** for the staging mesh + the in-cluster agent runner,
2. a **chaos-injection plan** (Chaos Mesh, with Litmus considered),
3. the **agent-runner harness** that drives experiments against a cluster and
   scores the agent's root-cause diagnosis.

Attempt everything safely runnable (offline harness self-test, `kubectl` dry-run,
YAML/RBAC validation). If live cluster access is unavailable, document the blocker
precisely and still ship a correct, runnable scaffold.

## Context found in repo
- `mreal/k8s.yaml` — a REAL call-mesh on GKE: gateway -> checkout -> payments -> db,
  plus orders -> db (fan-in). Faults propagate over real HTTP; gateway is the
  "loud victim". Prometheus ServiceMonitor + PrometheusRule already wired.
- `mreal/server.py` — services expose `/metrics`, `/healthz`, and a control plane
  `POST /ctl/fault?mode=error|slow` + `/ctl/heal`. This is the in-app fault hook.
- `gcp-bench/state/gke-kubeconfig.yaml` — kubeconfig to the live GKE cluster
  `rlvr-bench` (API server `https://136.114.32.127`), uses the gcloud exec-cred plugin.
- `rex/scoring.py:deterministic_judge` — the project's canonical diagnosis grader.

## Approach
- Treat Chaos Mesh as the **infra-level** fault injector that mirrors the app-level
  `/ctl/fault` taxonomy: HTTPChaos(abort)=error, HTTPChaos(delay)/NetworkChaos=slow,
  StressChaos on db=pool-exhaustion, PodChaos=availability fault. Each maps to one
  REx root-cause class so the agent is graded on the same rubric live and offline.
- Build the agent-runner with **two backends**: `kube` (live: apply chaos, scrape
  metrics, auto-delete) and `sim` (offline twin using the same dependency edges).
  The `sim` backend makes the whole harness runnable and CI-testable with no cluster.
- Reuse `rex/scoring.py` for grading; keep blast radius pinned to the namespace and
  every experiment time-bounded so faults structurally auto-heal.

## Files to create (all J1-namespaced; NO shared-core edits)
- `artifacts/j1_staging_deploy.yaml` — Namespace `j1-staging`, agent-runner Job,
  least-privilege ServiceAccount/Role/RoleBinding.
- `artifacts/j1_chaos_experiments.yaml` — 5 Chaos Mesh experiments.
- `artifacts/j1_agent_runner.py` — the harness (sim + kube backends + selftest).
- `j1_chaos_plan.md` (inside 06) — install/runbook + Chaos Mesh vs Litmus decision.

## Dependencies
kubectl, helm, gcloud (present); a reachable GKE cluster + Chaos Mesh CRDs (LIVE
path only). Python `yaml`, `rex.scoring` (present).

## Risks
- **Live access risk** (materialized): gcloud creds may be invalid / API server
  firewalled -> live path blocked. Mitigation: sim backend + dry-run validation.
- Chaos that outlives its window. Mitigation: bounded `duration` on every experiment
  + `finally`-delete in the harness + RBAC that can delete chaos but not workloads.
- Grading the loud victim instead of the root. Mitigation: red-herring lists in
  GROUND_TRUTH + deterministic_judge penalty.

## Success criteria
1. Manifests parse and pass structural + RBAC-invariant checks.
2. Harness self-test passes for all 5 experiments (oracle=True, red-herring=False).
3. Chaos plan documents install, safety, and the Chaos-Mesh-vs-Litmus choice.
4. Live blocker, if any, documented precisely (exact error, what was tried).
