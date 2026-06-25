# J1 — 08 Verification

## Success criteria from 01_plan.md
1. **Manifests parse and pass structural + RBAC checks** — ✅ Test 3 & 4. Both
   multi-doc YAMLs parse to the expected kinds; all required fields present; RBAC
   least-privilege invariant (heal-chaos-yes, delete-workloads-no) holds.
2. **Harness self-test passes for all 5 experiments** — ✅ Test 1. oracle=True,
   herring=False, victim identified, exit 0.
3. **Chaos plan documents install, safety, Chaos-Mesh-vs-Litmus** — ✅
   `j1_chaos_plan.md`: helm install runbook, the L0/L1 fault ladder, the
   Chaos-Mesh-vs-Litmus decision, and a 5-point structural safety contract.
4. **Live blocker documented precisely** — ✅ Test 6: exact gcloud "Account has been
   deleted" error + the API-server timeout (http_code=000), with what was tried and why
   other accounts weren't switched.

## Are the outputs real (not placeholder)?
- `j1_agent_runner.py` is **executed** (Tests 1, 2, 5, 7) — it runs, grades, and the
  primary path imports the real `rex.scoring.deterministic_judge` (Test 7 prints
  `rex.scoring import: OK` and `REPO -> /Users/mei/rl`).
- The two manifests are **parsed and structurally validated** against per-kind required
  fields, and the RBAC invariant is asserted programmatically — not eyeballed.
- The chaos experiments map to a REAL existing mesh (`mreal/k8s.yaml`) with a real
  control plane (`mreal/server.py` `/ctl/fault`), so the experiment design is grounded
  in the actual deployed topology, not invented.

## What is genuinely NOT verified (honest)
- No experiment was applied to a live cluster, no Chaos Mesh was installed, and no real
  Prometheus metric was scraped — blocked by dead gcloud auth AND an unreachable API
  server (Test 6). The `--backend kube` path and helm install are validated only as
  scaffolding (code review + offline parse), not by execution.
- `kubectl --dry-run` could not run because the project kubeconfig's exec-cred plugin
  fails before any client-side validation; an empty-kubeconfig client dry-run also fails
  because kubectl needs the API server for its RESTMapper. Offline validation was done
  via `yaml.safe_load_all` + structural assertions instead.

## Verdict
The three named deliverables (deployment manifest, chaos-injection plan, agent-runner
harness) are real, self-consistent, and validated to the maximum extent possible
offline. The single missing piece — execution against the live cluster — is blocked by
a precisely documented, external auth/network failure, not by a defect in the deliverable.
Status: **completed deliverable with a documented live-execution blocker.**
