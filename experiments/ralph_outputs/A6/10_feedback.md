# A6 — 10 Feedback for the next task

The CIDG scenario schema has a strict closed vocabulary (`sim/spec.py`:
`NODE_KINDS`/`EDGE_TYPES`/`ROOT_CAUSE_KINDS`/`SLO_DIRECTIONS` + tools from `tools_registry.json`),
and there is a ready-made gate — `python3 -m sim.spec validate <glob>` — so author the YAML, then
let the validator catch any out-of-vocab kind/edge/tool before claiming success; all 10 of mine
passed first try by copying the `70-facebook`/`72-knight` house style (root hub node + 2–4 victim
services + ingress LB, one buried `get_logs` smoking gun, a `scale_deployment` trap on a NON-root
victim, and the single correct fix tool on the root). Three reusable lessons for the next worker:
(1) when an incident's true fix has no tool (e.g. "restore from backup"), pick the closest in-vocab
action and explain the abstraction in `canonical_fix.ordering_notes` rather than inventing a tool
or faking the schema; (2) do a duplicate-`meta.id` scan across the whole `generated/` dir before
finishing, because parallel workers grab adjacent file numbers — use descriptive slugs, not just
numbers; (3) the validator only does *static* checks — it does not run `sim/engine.py::propagate()`,
so "validates" ≠ "cascade emerges at run time"; if a future task needs the emergent properties
proven, actually execute the engine on the spec. Metastable incidents (retry storms, ring churn)
need `rate_law.worsened_by` + `persistent: true` to model worsen-on-scale, which the simple leaf
template does not capture — flag that explicitly rather than pretending the cascade is faithful.
