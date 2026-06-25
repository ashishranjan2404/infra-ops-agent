# J1 — 06 Implementation

## Artifacts built (all under experiments/ralph_outputs/J1/artifacts/ — no shared-core edits)

### 1. `j1_chaos_experiments.yaml` — chaos-injection plan as CRs
5 Chaos Mesh experiments, each namespace-scoped to `cidg-mreal` and time-bounded:
- `j1-payments-error` (HTTPChaos abort) — twin of sim "error" at the root.
- `j1-payments-latency` (HTTPChaos delay 1200ms) — twin of sim "slow", matches the
  app's 1.2s slow sleep.
- `j1-db-pool-stress` (StressChaos cpu) — starves the 8-slot db semaphore -> fan-in
  degradation of payments AND orders.
- `j1-checkout-egress-delay` (NetworkChaos delay on checkout->payments) — partial
  degradation red herring (payments metrics look clean).
- `j1-gateway-pod-kill` (PodChaos pod-kill) — availability self-fault; agent must NOT
  chase upstreams.

### 2. `j1_staging_deploy.yaml` — deployment manifest
- Namespace `j1-staging` (staging twin; does not touch live `cidg-mreal`).
- `Job/j1-agent-runner` running the harness with `ttlSecondsAfterFinished` cleanup.
- Least-privilege `ServiceAccount` + `Role` + `RoleBinding`: can create/delete Chaos
  Mesh CRs (the heal path) and read/exec pods; **cannot delete pods/deployments**.

### 3. `j1_agent_runner.py` — the agent-runner harness (runnable)
- Two backends: `sim` (offline twin via the mesh topology; zero external deps) and
  `kube` (live: apply chaos -> soak -> scrape `/metrics` -> `finally`-delete to heal).
- Shared grader: `score()` delegates to `rex.scoring.deterministic_judge`, with a
  guarded offline fallback.
- `GROUND_TRUTH` carries gold root cause + red-herring terms per experiment so the
  grader penalizes blaming the loud victim.
- Agent contract: any shell command; observation JSON on stdin -> one-line diagnosis on
  stdout. Includes `--selftest` (no cluster, no agent) as the CI smoke path.

### 4. `j1_chaos_plan.md` — install runbook + Chaos-Mesh-vs-Litmus decision + safety contract.

## Proposed change to shared core (NOT applied — documented only)
No shared-core edit is required for J1. The harness imports `rex.scoring` read-only.
The live mesh and its `/ctl/fault` control plane already exist in `mreal/`. If we later
want the in-cluster Job (`--backend kube`) to run *inside* the cluster, the only change
is to base the runner image on one that ships `kubectl` (e.g. `bitnami/kubectl`) or use
the in-cluster python k8s client — that is an image/manifest change confined to
`j1_staging_deploy.yaml`, not a core edit. Captured here per the no-shared-edit rule.

## Live-cluster attempt
Attempted to reach the GKE cluster `rlvr-bench` via
`gcp-bench/state/gke-kubeconfig.yaml` (API server `https://136.114.32.127`). Both the
auth and the network path failed — see `07_test_results.md` for exact errors. The
deliverable was therefore validated through the offline `sim` backend, the harness
self-test, YAML structural checks, and the RBAC invariant check.
