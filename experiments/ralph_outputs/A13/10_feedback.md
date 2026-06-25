# A13 — Feedback for the next task

The CIDG environment is single-`root_cause` by construction: `sim/engine.py` injects exactly one
fault node and `is_resolved` checks only that node, so any new *capability* axis (multi-fault,
order-dependence, hysteresis chains) is data-authorable but inert until a matching engine change
lands. The clean pattern that worked here: author schema-valid YAMLs using a forward-compatible
extra block (which `sim.spec._build` silently tolerates), then deliver the engine change as a
verified `.patch` rather than editing shared core — and PROVE the mechanism on a throwaway copy
(`/tmp/.../b`) so the claim isn't cosmetic. Two gotchas for the next worker: (1) the generated dir
has MORE files than a naive `ls` page shows and numbers are reused across different names, so always
glob-check and pick a unique infix name to avoid collisions; (2) `assertions.cascades` and
`assertions.buried_gun_exists` are hard validate-gates — every spec needs ≥1 required/pool/queue edge
and ≥1 smoking_gun or `validate` fails. The obvious next task is a one-commit PR that applies
`engine_multifault.patch` and wires a `rex/scoring.py` test proving a 2-fix trajectory out-scores a
1-fix one; after that, add an order-coupled multi-fault spec (fix A unlocks diagnosing B).
