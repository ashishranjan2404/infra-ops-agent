# 10 — Feedback for the next task

The biggest lever in this corpus is **trap diversity, not taxonomy design**: 94% of
all 51 scenarios use `scale_deployment` as the trap, restart/rollback are token
instances, and failover is entirely absent — so any "avoid the trap" reward term
collapses to a single memorizable heuristic ("don't scale") that gives no
within-group spread. If a downstream task touches the synthetic generator
(`harness_synth`/CIDG), it should assign trap verbs *per failure class* (rollback on
FD-exhaustion, restart on cert-expiry, a real failover-trap on shared-cert cascades)
to make trap-avoidance a genuine reasoning signal. Operationally: reusing a prior
task's artifact (G4's `trap_taxonomy.json`) as input saved real work and kept counts
consistent across tasks — prefer composing on existing task outputs over re-deriving.
And the flat `TRAP_PENALTY=0.60` means a trap *category* buys diagnostics, not reward
shaping, unless someone proposes severity-weighted penalties in `rex/scoring.py`.
