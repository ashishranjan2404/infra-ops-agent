# J6 — 04 Technical Spec

## A. Scenario YAML — `scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml`

Schema = `sim/spec.py:ScenarioSpec` (validated by `sim.spec.validate`).

### Topology (4 nodes, 3 edges)
| node | kind | role |
|------|------|------|
| `chrono-ntp` | `control_plane` | **root**: skewed NTP clock (the hidden fault) |
| `lease-quorum` | `pool` | distributed-lock / leader-lease service |
| `order-api` | `service` | loudest victim (split-brain double-writes) |
| `ledger-api` | `service` | second victim |

| edge | type | rationale |
|------|------|-----------|
| `lease-quorum → chrono-ntp` | `discovery` | lease validity trusts the clock (control-plane dep; propagates error) |
| `order-api → lease-quorum` | `required` | a valid single leader lease is required to serve writes |
| `ledger-api → lease-quorum` | `required` | same |

> Note: `required`/`discovery` are the only edge types `sim/engine.py` propagates error through
> (`_error_edges`). `pool`/`queue` edges do NOT carry error in Tier-A — so victim edges MUST be
> `required` for the cascade to fire. (This is the single most important modeling fact for J6.)

### root_cause
```yaml
location: chrono-ntp
kind: dns_race          # closed-vocab timing/race class; here = CLOCK skew
severity: 0.75
hidden: true
persistent: false       # Tier-A clears on correct root fix (no hysteresis modeled)
```

### fault / SLO / trap / fix
- fault: `exec` inject `clock skew (+1100ms)`; sim `set: {dns_race_active: true}`.
- SLO: `error_rate_pct >= 5` on `order-api` and `ledger-api` (`higher_bad`, sustain 3).
- trap_actions: `scale_deployment order-api replicas:8` (adds lease contenders → worsens).
- canonical_fix: `restart_service chrono-ntp` (re-sync clock + re-elect single leader).
- smoking_gun: `get_logs` on `chrono-ntp`, signature `"clock offset +1100ms exceeds lease skew
  bound; leader lease invalidated"`, buried_under 45.

## B. Engine contract (read-only, `sim/engine.py`)
- `World(spec, inject=True)`: sets `own_error[root]=severity`; `propagate()` multiplies error
  through `required`+`discovery` edges.
- `apply_action(world, Action(tool, args))`: clears root iff
  `tool ∈ REMEDIATION[kind] and args.target == fault_node`.
- `is_resolved(world)` == `root_cleared and SLOs back under threshold`.
- `REMEDIATION['dns_race'] == {modify_network_policy, restart_service}` — both clear the root on
  the root node (recorded caveat).

## C. Sim driver — `run_novel_sim.py`
```
load_spec(path) -> validate() == []          # check 1
World(inject) -> victim err > 5 each          # check 2 cascades
World(inject) + trap         -> ¬is_resolved  # check 3
World(inject) + clear_cache@root -> ¬resolved # check 4 wrong tool
World(inject) + restart@victim  -> ¬resolved  # check 5 wrong target
World(inject) + restart@root    ->  resolved  # check 6 canonical fix
engine_note: modify_network_policy@root -> resolved (recorded, not a pass/fail)
```
Exit 0 iff `{valid, cascades, ¬start, ¬trap, ¬wrong_tool, ¬wrong_target, fix}` all hold.

## D. Agent driver — `run_novel_agent.py`
- `register_in_memory()` adds an entry to `rex.harness._SCENARIOS` (style `cascade`, gold_root =
  NTP narrative, red_herrings = network partition / scale order-api / bad deploy, fix_tools =
  `[restart_service]`, traps = scale order-api). **No disk write.**
- `propose_fn = functools.partial(rex.loop.propose, model=<gateway model>)` (the default model is
  captured at def-time, so partial is required to override it).
- `refine_loop(sc, budget=4, propose_fn=propose_fn, log=trace.append)` → returns
  `{iterations, best_score, best_iter, resolved, clean_win}`.
- Re-grade the best plan with `rex.scoring.score_plan(plan, sc, run_plan(plan, sc))` → `(reward, fb)`.
- `generalizes := reward >= 0.8`. Run models `glm-5p2`, `minimax-m3`, `deepseek-v4-pro`.

## E. Test cases
| id | input | expected |
|----|-------|----------|
| T1 | `sim.spec validate` on YAML | `1/1 specs valid` |
| T2 | inject | both victims `error_rate_pct` > 5 |
| T3 | trap only | `is_resolved == False` |
| T4 | `clear_cache@root` | `is_resolved == False` |
| T5 | `restart_service@order-api` | `is_resolved == False` |
| T6 | `restart_service@chrono-ntp` | `is_resolved == True` |
| T7 | agent, glm-5p2 | reward ≥ 0.8, diagnosis_correct, no trap |
