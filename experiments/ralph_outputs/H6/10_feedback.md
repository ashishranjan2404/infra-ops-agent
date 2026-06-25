# H6 — 10 Feedback for the next task

The repo's `sim/spec.py` is the authoritative loader/validator (`load_spec`, `validate`, and a
`python -m sim.spec validate <glob>` CLI) and `sim/engine.py` exposes `World.from_spec` /
`apply_action` / `World.run` — reuse these read-only rather than re-deriving schema rules; the
closed vocabularies (NODE_KINDS, EDGE_TYPES, ROOT_CAUSE_KINDS, SLO_DIRECTIONS) and the
REMEDIATION map in the engine are the ground truth. The scenario corpus is dual-located:
`scenarios/cidg/*.yaml` (10 curated) + `scenarios/cidg/generated/*.yaml` (51), 61 total, all
currently schema- and engine-valid. When building any validator/CI gate, the *negative path* is
where the value is — author deliberately-broken fixtures and assert exit codes, because an
all-green corpus makes the positive run low-signal. Watch the seam between "acceptance" (loads +
runs, this task) and "semantics" (fix actually resolves, A16's task) and state which you're
checking; `apply_action` returning normally does NOT mean the fix worked. Note `validate()`
catches unknown-SLO-victim and most structural errors *before* the engine, so engine-stage
failures are rare in practice. Parallel-safety rule held cleanly: this task needed zero core
edits, so no `.patch` workaround was required.
