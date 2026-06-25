# J6 — 10 Feedback for the next task

The biggest time-saver is reading `sim/spec.py` + `sim/engine.py` BEFORE authoring any scenario:
the engine only propagates error through `required`/`discovery` edges (`pool`/`queue` carry none),
and it clears a root only when `tool ∈ REMEDIATION[kind] AND target == fault_node` — so a scenario
whose cascade or fix doesn't fire is almost always an edge-type or REMEDIATION-membership mismatch,
not a logic bug. "Novelty" in CIDG is bounded by the closed `ROOT_CAUSE_KINDS`, so a genuinely new
incident must be novel in *mechanism/topology/narrative* mapped onto the nearest kind, and you should
disclose any place where the shared engine physics doesn't enforce your story (e.g. a kind whose
REMEDIATION set admits a tool your narrative says is wrong) rather than overclaim. For reaching the
agent path without touching shared state, register the scenario in the in-memory `rex.harness._SCENARIOS`
dict and override the loop's model with `functools.partial(propose, model=...)` (the module-global
`_SMALL_MODEL` is captured at def-time and ignored); route to a HUD-gateway model since direct
Anthropic is out of credits, and rely on the default P0 *deterministic* judge so grading needs no LLM.
Always run ≥3 frozen models plus negative controls (trap / wrong-tool / wrong-target) so a clean win
is evidence, not a single-policy artifact.
