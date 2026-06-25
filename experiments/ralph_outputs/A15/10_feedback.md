# A15 — Feedback for the next task

The CIDG spec already reserves clean hooks for observation-degradation variants
(`observation.alerting`, `observation.monitoring_degrades`, `smoking_guns[*].buried_under`,
`assertions.monitoring_degrades`), so a "noisy/degraded" variant is a *populate-the-schema*
task, not a new-mechanism task — lean on the existing fields. Two gotchas to carry forward:
(1) `assertions.monitoring_degrades=True` is invalid without an `observes` edge (sim/spec.py:350),
so any monitoring-degradation transform must inject a monitoring node + observes edge when the
baseline lacks one; and (2) the fast-sim `propagate()` derives metrics purely from
topology+fault and does NOT read the alerting/buried_under fields, so observation-only variants
are reward-invariant but behaviorally latent until the observation/tool layer is wired to consume
them — state this scope honestly rather than claiming a behavioral delta. For reproducibility,
always ship a transform-from-baseline script (validated by round-tripping through
`sim.spec._spec_from_dict`+`validate`, with repo-root added to sys.path so it runs cwd-independent)
plus pytest, and write outputs to the task artifacts dir, never into `scenarios/cidg/generated/`.
