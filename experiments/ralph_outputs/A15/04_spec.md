# A15 — Technical Spec

## Data model (from sim/spec.py, unchanged — we only populate it)
```
Observation:
  alerting: str = "uniform"          # we set -> "noisy"
  monitoring_degrades: bool = False  # we set -> True
  smoking_guns: list[SmokingGun]     # we deepen buried_under
SmokingGun:
  tool: str; node: str; signature: str; buried_under: int = 0
Assertions:
  ... monitoring_degrades: bool = False   # we set -> True
Edge(type ∈ {required,optional,pool,queue,discovery,observes})
```
Schema constraint enforced at sim/spec.py:350:
`assertions.monitoring_degrades=True` ⇒ at least one edge with `type=="observes"`.

## Function signatures (artifacts/noisy_metrics_transform.py)
```python
BURIED_MULT = 3
BURIED_FLOOR = 20
MONITOR_NODE = "monitoring-stack"

def transform(doc: dict) -> dict        # PURE: returns new deepcopy, input untouched
def _root_node(doc: dict) -> str        # head of root_cause.location ("A->B" -> "A")
def _ensure_observes_edge(doc) -> bool  # adds monitoring node + observes edge iff none; True if modified
def _validate(doc: dict) -> list[str]   # round-trips through sim.spec._spec_from_dict + validate
def main(argv: list) -> int             # CLI
```

## Transform contract
| field | before | after |
|---|---|---|
| meta.id | `X` | `X-noisy` (idempotent — no double suffix) |
| meta.derived_from / variant | – | `X` / `noisy_metrics` |
| observation.alerting | `uniform` | `noisy` |
| observation.monitoring_degrades | False | True |
| smoking_guns[i].buried_under | `b` | `max(b*3, 20)` |
| assertions.monitoring_degrades | False | True |
| topology (if no observes edge) | – | + `monitoring-stack` node + `observes`→root node |
| root_cause, canonical_fix, slo, fault | unchanged | unchanged |

## CLI
```
python noisy_metrics_transform.py <baseline.yaml> -o <out.yaml>   # write
python noisy_metrics_transform.py <baseline.yaml> --check          # validate only, exit 0/1
```
Validation failure ⇒ nonzero exit + errors on stderr; never writes an invalid file.

## Test cases (pytest)
1. `test_sets_noisy_observation` — alerting=noisy, both monitoring_degrades flags True.
2. `test_buries_smoking_guns_deeper` — buried_under == max(before*3, 20), ≥ before.
3. `test_injects_observes_edge_for_validity` — an observes edge exists post-transform.
4. `test_does_not_mutate_input` — input dict byte-equal to a pre-call snapshot.
5. `test_physics_unchanged` — root_cause & canonical_fix identical; original nodes ⊆ new nodes;
   non-observe edges == original edges.
6. `test_transformed_specs_validate` — both a with-gun and no-gun baseline validate clean.
7. `test_idempotent_id` — applying twice doesn't append `-noisy` twice.

## File format
Output is a standard CIDG scenario YAML (`yaml.safe_dump`, `sort_keys=False`), loadable by
`sim.spec.load_spec`, runnable anywhere a baseline scenario is.
