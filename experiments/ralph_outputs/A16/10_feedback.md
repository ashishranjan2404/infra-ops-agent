# A16 — Feedback for the next task

Don't trust a scenario's self-declared `assertions.*` flags — the spec-level
validator (`sim.spec.validate`) only checks structure and closed vocab; it never
runs the fix, so authoring bugs like wrong-target or wrong-tool-for-kind sail
through. The engine's real physics live in two places worth memorizing: the
`REMEDIATION` table in `sim/engine.py` (which tool clears which root-cause kind)
and the rule that `apply_action` clears the root ONLY when `target ==
_fault_node`, where `_fault_node = root_cause.location.split("->")[0]` for
edge-located faults. Two recurring defect classes to expect: (a) fixes that
target the dependent/symptom node instead of the fault node, and (b) SLOs naming
metrics the engine doesn't model (only `error_rate_pct` + `p99_latency_ms` exist),
which KeyError. Also: the scenario directory is mutating live under parallel
workers — always glob and report the actual count, never hardcode a number from
the task title, and treat your report as a timestamped snapshot. Finally, the
engine ignores `persistent`/`reset_by` hysteresis, so a "pass" on those is
engine-faithful but not physically complete — flag it rather than over-claim.
