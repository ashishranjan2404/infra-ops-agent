# J1 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer 1 — "the skeptic" (finds real gaps)
**Problems found:**
- G1: The `sim` backend's `loudest_victim` is *always* gateway for cascades (it's the
  top of the chain and the depth multiplier `×3` guarantees it). So the "baseline =
  blame loudest victim" is trivially gateway every time — that's fine as a *foil*, but
  the test should prove the grader rejects "gateway" for a payments-root experiment,
  not just that it accepts the gold. **Fix:** the self-test already checks
  `herring=False` where `herrings[0]` is the victim — confirmed it asserts the foil
  fails. Keep.
- G2: `_kube_observe` scrapes `localhost:8080/metrics` via `kubectl exec` — but the
  loadgen drives traffic at `gateway`/`orders`, so leaf services (db) may have low
  request counts and a noisy `err_rate`. **Fix:** documented `soak_s` (default 30s) so
  counters accumulate; acknowledged db ratios are lower-confidence.
- G3: HTTPChaos requires the Chaos Mesh sidecar/iptables interception to be enabled for
  the target pods; on some clusters HTTPChaos needs the pods annotated. **Fix:**
  noted in the chaos plan that NetworkChaos/StressChaos/PodChaos are CNI/kubelet-level
  and need no app cooperation, while HTTPChaos is the highest-fidelity but most
  install-sensitive — listed as a fallback ladder.

## Engineer 2 — "the integrator" (finds wiring/ambiguity)
**Problems found:**
- I1: `REPO = Path(__file__).resolve().parents[4]`. The file is at
  `rl/experiments/ralph_outputs/J1/artifacts/j1_agent_runner.py` -> parents[4] = `rl`.
  Verified by counting: artifacts(0)->J1(1)->ralph_outputs(2)->experiments(3)->rl(4).
  Correct, but brittle if moved. **Fix:** acceptable for a task-namespaced artifact;
  documented the assumption.
- I2: `_kube_observe` splits the YAML on `"\n---\n"` and matches `f"name: {experiment}\n"`.
  If two CRs shared a name prefix this could mis-match. Names are unique and full-line
  matched with trailing `\n`. OK.
- I3: The deploy Job runs `--backend kube` but the image `python:3.11-slim` has no
  `kubectl`. **Real gap.** **Fix:** documented in 06 — the in-cluster Job path requires
  a kubectl-bearing image (e.g. `bitnami/kubectl` base) OR using the in-cluster API via
  a python client; for this deliverable the harness is validated via the *local* kube
  path (operator runs it from a workstation with kubectl). Flagged as a known follow-up.

## Engineer 3 — "the reviewer" (over/under-engineering)
**Problems found:**
- R1: Five experiments is the right breadth (error/latency/pool/network/availability) —
  not over-scoped. Good.
- R2: The offline grader fallback duplicates logic that `deterministic_judge` owns.
  **Decision:** keep it but ONLY as a fallback guarded by `try/except`, so the primary
  path is always the shared grader. Confirmed live test uses the real import.
- R3: No retry/backoff on `kubectl exec` flakes. For an eval harness a single failed
  scrape should mark the app `None`, not crash the run — **already handled** by the
  per-app `try/except` returning `{"err_rate": None, ...}`.

## Final filtered spec deltas
- Keep self-test asserting both oracle-pass and foil-fail (G1).
- Document soak + low-confidence leaf metrics (G2), HTTPChaos install sensitivity +
  fault ladder (G3).
- **Flag the in-cluster Job needs a kubectl image** (I3) — the validated path is the
  workstation/local kube backend; the Job manifest is provided as the deployment
  target shape.
- Shared grader primary, fallback guarded (R2); per-app failure tolerance (R3).
