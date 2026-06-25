# SUMMARY — Task I7: Trap-action taxonomy

## What got done
Built a 4-family trap taxonomy (scale-trap, restart-trap, rollback-trap,
failover-trap, + other-trap catch-all), grounded in rex/scoring.py
(_traps_in() matches traps on tool; flat TRAP_PENALTY=0.60; format_feedback
why-table) and the scenarios/cidg/generated/*.yaml trap_actions: blocks. Reused
G4's trap_taxonomy.json as the input record set.

## Artifacts (experiments/ralph_outputs/I7/artifacts/)
- trap_taxonomy_doc.md — structured taxonomy + honest assessment
- classify_traps.py — read-only classifier (ran, exit 0)
- test_classify_traps.py — 4 tests, all pass
- trap_classification.json — generated output

## Result (measured over 51 scenarios)
| Category | Count | Share |
|---|---|---|
| scale-trap | 48 | 94.1% |
| restart-trap | 2 | 3.9% |
| rollback-trap | 1 | 2.0% |
| failover-trap | 0 | 0.0% |
| other-trap | 0 | 0.0% |

## Honest headline
The corpus is severely scale-trap-skewed (94%) and has zero failover-trap
coverage. Trap-avoidance reward here collapses to one heuristic ("don't scale");
real signal needs the generator to diversify trap verbs per failure class. The
taxonomy is descriptive/diagnostic — the penalty is flat, so it adds no reward
axis on its own.

Status: completed.
