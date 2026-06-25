# Trap-Action Taxonomy (SRE-Degrees / REx)

A **trap action** is a remediation that looks plausible to a frontier model under
incident pressure but does **not** address the root cause — and in the scored
environment it costs a flat `TRAP_PENALTY = 0.60` (see `rex/scoring.py`,
`_traps_in()` / `score_plan()`). Each scenario YAML declares its trap(s) under
`trap_actions:` as `(tool, args.target)`; the judge fires when an applied action
matches that `(tool, target)` pair (target `None` = any target).

This taxonomy names four trap *families* by the **tool** the model reaches for.
The tool is the load-bearing signal because `_traps_in()` matches on tool first.

## Categories

| Category | Trap tools | Mechanism (why it's a trap) | Grounded in |
|---|---|---|---|
| **scale-trap** | `scale_deployment` | Adds replicas/capacity to a fault capacity cannot fix. For a per-process leak every new replica OOMs identically; scaling a crash-looping control plane *herds* its datastore and worsens recovery. | `format_feedback` why-table: "scaling does not address the root cause …" |
| **restart-trap** | `restart_service`, `restart_pod` | Bounces a process without removing the cause — the bad config/expired cert/leak returns on restart; blindly restarting a control plane re-triggers the crash. | why-table: "blindly restarting the control plane … WORSENS the outage" |
| **rollback-trap** | `rollback_deployment` | Reverts a deployment when the *active deploy is not the cause* (e.g. an expired cert, an FD leak). Burns time and can revert an unrelated good change. | a11-pair cert-expire scenario (gold fix = `renew_certificate`, trap = `rollback_deployment`) |
| **failover-trap** | `failover`, `promote_replica`, `switch_to_standby`, `drain_node` | Flips traffic to a standby/secondary that shares the *same* fault (same cert, same poison message, same upstream partition) — the failover target fails identically. | Mapped for completeness; **0 instances in current corpus** (see distribution). |
| `other-trap` | (catch-all) | Any trap tool not yet mapped. Degrades honestly instead of dropping rows. | — |

## How a scenario maps to a category

1. Read the scenario's first declared `trap_actions[0].tool`.
2. Look it up in `TOOL_TO_CATEGORY` (`classify_traps.py`).
3. Unknown tool → `other-trap`.

The contrast is always **trap tool vs. gold fix tool** (the scenario's
`canonical_fix` / `correct_fix_tools`): e.g. cert-expiry's gold fix is
`renew_certificate` and its trap is "scale the gateway" — same target, wrong verb.

## Distribution (measured, see `trap_classification.json`)

| Category | Count | Share |
|---|---|---|
| scale-trap | 48 | 94.1% |
| restart-trap | 2 | 3.9% |
| rollback-trap | 1 | 2.0% |
| failover-trap | 0 | 0.0% |
| other-trap | 0 | 0.0% |

## Honest assessment of the distribution

The corpus is **severely skewed toward scale-trap (94%)**. This is a real,
documented weakness of the current taskset, not a property of the taxonomy:

- The synthetic generator (`harness_synth`/CIDG) reaches for `scale_deployment`
  as the default "looks-busy but useless" action for almost every failure class,
  so 48 of 51 scenarios share the *same* trap verb.
- **failover-trap has zero coverage.** No scenario tests whether a model wrongly
  fails over to a standby that shares the fault — arguably the most dangerous
  real-world trap (it spreads blast radius). The category is defined and the tool
  map is ready, but the taskset cannot currently exercise it.
- restart-trap (2) and rollback-trap (1) are token instances, mostly from the
  hand-built a11 cert-expiry pair.

**Implication for training:** a model can score well on the trap-avoidance term by
learning a single heuristic — "don't scale" — without learning the more general
"don't apply a capacity/restart/rollback/failover verb to a fault that verb can't
fix." To make trap-avoidance a real signal, the generator should diversify trap
verbs per failure class (e.g. rollback-trap on FD-exhaustion, failover-trap on
shared-cert cascades) so all four families are represented and within-group reward
spread reflects genuine reasoning, not one memorized "no" word.
