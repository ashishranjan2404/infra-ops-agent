# J1 — SUMMARY

## Task
Deploy the SRE/REx agent in a staging K8s cluster with real chaos injection. Deliver a
deployment manifest, a chaos-injection plan, and an agent-runner harness against a cluster.

## Delivered (all task-namespaced under experiments/ralph_outputs/J1/artifacts/)
1. j1_staging_deploy.yaml — deployment manifest: j1-staging namespace + agent-runner Job
   + least-privilege RBAC (can heal chaos, cannot delete workloads — verified).
2. j1_chaos_experiments.yaml — chaos-injection plan as 5 Chaos Mesh CRs (HTTPChaos
   error/latency, StressChaos pool-exhaustion, NetworkChaos red-herring, PodChaos
   availability), each namespace-scoped and time-bounded for structural auto-heal.
3. j1_agent_runner.py — agent-runner harness with sim (offline twin) and kube (live)
   backends, the project's shared rex.scoring.deterministic_judge grader, per-experiment
   ground truth with red-herring penalties, a baseline foil, and --selftest.
4. j1_chaos_plan.md — helm install runbook, the L0/L1 fault ladder, the
   Chaos-Mesh-vs-Litmus decision, and a 5-point safety contract.

## Validation (all real, executed)
- Harness self-test: 5/5 experiments PASS (oracle=True, red-herring=False).
- Manifests: parse to expected kinds; per-kind required fields present; RBAC invariant holds.
- Grader: real rex.scoring import confirmed (not the fallback).

## Blocker (live execution only)
The live GKE cluster rlvr-bench could not be reached: (a) gcloud auth is dead — active
account devstar4126@gcplab.me returns "invalid_grant: Account has been deleted", and the
kubeconfig's exec-cred plugin fails before any kubectl call; (b) the API server
136.114.32.127:443 times out unauthenticated (private/firewalled endpoint). So Chaos Mesh
install, live --backend kube, and kubectl --dry-run could not run. The deliverable is
validated offline via the sim twin; the live cluster was NOT touched or disrupted.

## Status: completed (deliverable real + validated; live run blocked & documented)
