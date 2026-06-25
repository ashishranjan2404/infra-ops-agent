# J1 — 03 Improved Plan

## What changed after the grill

### Accepted critiques
- **(AAAI) Ship a baseline.** Added the "always-blame-loudest-victim" trivial agent
  as the agent-to-beat, plus red-herring lists in `GROUND_TRUTH` so the deterministic
  grader penalizes diagnosing the loud victim. The self-test now asserts
  `oracle=True AND red_herring=False` for every experiment — a real evaluation
  contrast, not just a demo.
- **(PSRE + SMR) Shared grader, not rigid shared observation.** Both backends call
  `rex.scoring.deterministic_judge`. The `kube` backend is explicitly allowed to emit
  `None`/partial values (scrape gaps, killed pods) instead of being forced to mimic
  sim. This preserves the reason to leave sim.
- **(DOL) Fault ladder, both layers kept.** Documented L0 (`/ctl/fault`, app smoke,
  no Chaos Mesh) and L1 (Chaos Mesh infra faults). Not a conflict — complementary
  fidelity. The chaos plan presents them as a ladder.
- **(PSRE + DOL) Safety hardening.** Every experiment carries a bounded `duration`;
  the harness deletes the experiment in a `finally` (auto-heal even on crash); the
  Role can `delete` chaos CRs but has **no** `delete` on pods/deployments — verified
  by an assertion in testing.
- **(PSRE) Justify `mode: all` on payments.** Documented inline: single-replica
  faults get masked by the Service load-balancer, so the error/latency experiments
  hit all payments replicas; `PodChaos` keeps `mode: one` (availability fault).

### Rejected critiques (with reasons)
- **(RLE) "Observation must be byte-identical across backends."** Rejected. The
  point of infra eval is messier real signals; sanding them to match sim defeats it.
  We keep the schema's *shape* shared but allow `kube` noise/`None`s. RLE's
  contamination worry is mitigated by sharing the *grader*, which is the part that
  actually determines the comparison.
- **(AAAI) "RL hygiene is over-engineering here."** Partially rejected. We keep one
  shared observation dataclass (cheap, prevents two grading code paths) but drop the
  heavier "backend-invariant distribution" requirement RLE wanted.

## Net plan (unchanged core, hardened edges)
1. `j1_staging_deploy.yaml`: `j1-staging` ns, agent-runner Job, least-priv RBAC.
2. `j1_chaos_experiments.yaml`: 5 namespace-scoped, time-bounded Chaos Mesh CRs.
3. `j1_agent_runner.py`: sim + kube backends, shared grader, selftest, baseline.
4. `j1_chaos_plan.md`: install runbook, the fault ladder, Chaos-Mesh-vs-Litmus
   decision, safety contract.
5. Validate offline; attempt live; report the cluster blocker precisely.
