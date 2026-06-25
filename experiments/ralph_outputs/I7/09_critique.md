# 09 — Honest Critique

## What's weak
1. **The taxonomy is mostly a lookup table.** Classification is a dict map on tool
   name. There's no semantic inference — a genuinely novel trap tool lands in
   `other-trap` with no further reasoning. This is intentional (hermetic, testable)
   but a reviewer can fairly call it thin.
2. **94% scale-trap means the data, not the taxonomy, is the bottleneck.** The most
   honest reading of this task is: the taxonomy is fine, but the *taskset* it
   describes is degenerate for trap-avoidance. My deliverable correctly diagnoses
   this but cannot fix it without editing the generator/scenarios (forbidden here).
3. **failover-trap has zero instances.** A whole category exists only on paper. The
   four failover tool names (`failover`, `promote_replica`, …) are my invention, not
   tools the sim actually implements — I could not verify they'd ever be emitted.
4. **Single-trap-per-scenario assumption.** I read `trap_actions[0]` only. True for
   the current corpus but would undercount multi-trap scenarios.
5. **Flat penalty undercuts the point.** Because `TRAP_PENALTY` is a flat 0.60, the
   taxonomy carries no reward signal today — it's purely descriptive. A skeptic asks
   "so what does naming these buy us?" Answer: it's a diagnostic that exposes the
   skew; it does not change training dynamics on its own.

## What a reviewer attacks
- "You classified on a field you could have grepped." — Fair; the *value* is the
  honest distribution + the failover gap, not the mapping.
- "failover-trap is vaporware." — Partly true; labeled as 0-coverage/completeness.

## What's missing
- A proposal turned into an actual patch/scenario to add failover/rollback traps
  (left as doc suggestion to respect the no-shared-edit rule).
- Cross-tab of category × failure_class (G4's minimal records dropped failure_class,
  so I'd need the YAML scan path to enrich it; deferred).

## Net
Solid, honest, runnable diagnostic. Its main contribution is *exposing* that
trap-avoidance in this corpus is a one-word ("don't scale") heuristic — not a
glossy "four balanced categories" story.
