# A13 — Technical Spec

## 1. YAML schema (existing, from `sim/spec.py`)
Top-level keys consumed by `_spec_from_dict`: `meta`, `topology.{nodes,edges}`, `root_cause`,
`fault`, `slo[]`, `canonical_fix.{steps,ordering_notes}`, `observation`, `trap_actions[]`,
`paired_positive`, `assertions`, `chance`, `seed`. Unknown top-level keys are tolerated by
`yaml.safe_load` and never indexed, so adding `secondary_faults` is safe.

### Closed vocabularies (validation rejects outside these)
- `node.kind ∈` service, datastore, cache, queue, pool, control_plane, monitoring, node, lb, external
- `edge.type ∈` required, optional, pool, queue, discovery, observes
- `root_cause.kind ∈` cpu_starve, mem_leak, pool_leak, thread_exhaust, fd_exhaust, churn_spike,
  config_bloat, bad_content, bad_revision, cert_expire, cache_flush, disk_fill, node_notready,
  net_delay, dns_race, dep_revoked, defense_amplify, host_agent_crash
- `slo.direction ∈` higher_bad, lower_bad
- tools must be in `tools_registry.json` (25 tools incl. restart_service, rollback_deployment,
  clear_cache, renew_certificate, scale_deployment, increase_memory_limit, ...).

## 2. New block: `secondary_faults`
```yaml
secondary_faults:
  - location: <node-name>          # MUST differ from root_cause.location and from each other
    kind: <root_cause_kind>        # closed vocab
    severity: <float 0..1>
    fix_tool: <tool in REMEDIATION[kind] ∩ tools_registry>
    slo_node: <node-name>          # the SLO victim for this fault
```
Semantics (when `engine_multifault.patch` is applied): the engine injects
`own_error[location]=severity` for the primary AND every secondary; `is_resolved` becomes
`all(own_error[loc]==0 for loc in fault_locations) and _slo_ok`. Without the patch, the block is
inert (dropped) and the spec behaves as a faithful single-fault scenario on the primary.

## 3. The three specs (REMEDIATION mapping enforced)
`REMEDIATION` (engine physics): cert_expire→renew_certificate; pool_leak→{restart_service,restart_pod};
bad_revision→rollback_deployment; cache_flush→clear_cache; fd_exhaust→{restart_service,restart_pod};
cpu_starve→{scale_deployment,increase_memory_limit}.

| id | primary fault (loc/kind/fix) | secondary fault (loc/kind/fix) | shape |
|----|------------------------------|--------------------------------|-------|
| 80 | auth-gw / cert_expire / renew_certificate | session-pool / pool_leak / restart_service | independent |
| 81 | api-edge / bad_revision / rollback_deployment | result-cache / cache_flush / clear_cache | masking |
| 82 | conn-router / fd_exhaust / restart_service | rank-svc / cpu_starve / scale_deployment | shared victim |

Each: primary location is `root_cause.location` (engine-injected today); secondary in
`secondary_faults`. Each fault has a dedicated `slo` entry on its victim, and a dedicated
`canonical_fix.steps` entry. `assertions.buried_gun_exists=true` requires ≥1 smoking_gun → provide
two (one per fault).

## 4. Function signatures touched (proposed patch only)
```python
# sim/engine.py  (PROPOSED, delivered as .patch, NOT applied)
class World:
    def __init__(self, spec, inject=True):
        ...
        self._fault_nodes = [self._fault_node] + [
            sf["location"] for sf in getattr(spec, "secondary_faults", []) ]
        if inject:
            for loc, sev in self._fault_severities():
                self.own_error[loc] = sev
    @property
    def all_roots_cleared(self):
        return all(self.own_error[n] == 0.0 for n in self._fault_nodes)
def is_resolved(world):
    return world.all_roots_cleared and _slo_ok(world)
```
(Plus a `secondary_faults` field on `ScenarioSpec` populated in `_spec_from_dict`.)

## 5. Test cases (`artifacts/test_multifault.py`, pytest)
- `test_specs_validate`: every new YAML → `validate(load_spec(p)) == []`.
- `test_two_distinct_fault_locations`: primary loc + each secondary loc all distinct, count==2.
- `test_each_fault_has_slo_victim`: union of SLO `node`s covers both fault victims.
- `test_each_fault_has_fix_step`: a canonical_fix step targets each fault location with a tool in
  `REMEDIATION[kind]`.
- `test_primary_runs_unpatched`: `World.from_spec` builds, cascades (some non-victim node error>0),
  and applying the primary canonical fix clears the primary node + `root_cleared` is True.

## 6. File formats / parse contract
All YAMLs UTF-8, 2-space indent, no tabs, mirror the field order of existing specs (`40-*.yaml`).
`python -m sim.spec validate scenarios/cidg/generated/8?-*.yaml` must print `OK` for each and
`3/3 specs valid`.
