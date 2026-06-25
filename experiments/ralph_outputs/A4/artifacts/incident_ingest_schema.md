# Incident Ingest Schema — partner data contract (v1.0)

This is the data contract we hand a partner (e.g. Snorkel) so their incident
records drop straight into the SRE-Degrees pipeline. It is a **superset** of the
fields already used by:

- `scenarios/cidg/generated/*.yaml` — `root_cause`, `trap_actions`,
  `canonical_fix`, `slo`, `assertions`, `topology`, `chance`, `seed`
- `opensre-traj/real-incidents/catalog.md` — `loud_symptom`, `why_misleading`,
  `causal_chain`, `category`, trap/fix narrative
- `experiments/INCIDENT_DATASET.md` — `classification` taxonomy
  (`simple` / `cascade` / `novel`)

So a normalized partner record is convertible to a runnable scenario YAML with a
mechanical mapping (`root_cause`/`trap_actions`/`canonical_fix`/`slo`/`assertions`
pass through 1:1; `loud_symptom`/`why_misleading`/`causal_chain`/`category` come
from the catalog-style narrative fields).

## Required fields
| Field | Type | Notes |
|---|---|---|
| `schema_version` | string `N.N` | e.g. `"1.0"` |
| `incident_id` | slug `^[a-z0-9-]+$` | unique |
| `source` | object | provenance + **legal/PII metadata** (see below) |
| `title` | string | human title |
| `category` | enum | network_fault, config_error, saturation, resource_exhaustion, data, conflict, time, cache_flush, other |
| `classification` | enum | simple / cascade / novel |
| `loud_symptom` | string | the misleading alert |
| `root_cause` | object | `{location, kind, severity∈[0,1], hidden?, persistent?}` |
| `causal_chain` | array<string> | ≥1 step, symptom→cause path |
| `trap_actions` | array<{tool,args}> | actions a verifier asserts **do NOT** resolve |
| `canonical_fix` | object | `{steps:[{tool,args}], ordering_notes?}` — verifier asserts **resolves** |
| `slo` | array<{metric,node,direction,threshold,sustain_ticks≥1}> | failure detection |
| `assertions` | object<bool×6> | cascades, loudest_alert_not_cause, fix_resolves, buried_gun_exists, hysteresis, monitoring_degrades |

### Conditional
- If `classification == "cascade"`, `why_misleading` (string) is **required**.

### `source` sub-object (the legal/PII gate, in-band)
`{ org, kind(postmortem|raw_anon|env|reconstructed), url?, license,
   anonymization, pii_status(none|redacted|present) }`
Ingestion policy: **reject any record with `pii_status == "present"`.**

### Optional
`topology`, `observation`, `chance`, `seed`, `notes` (pass-through to scenario YAML).

## Tool vocabulary
`x-recommended-tools` lists tools the simulator already binds (`scale_deployment`,
`clear_cache`, `rollback_deployment`, `restart_pod`, `drain_node`, …). Partners may
use other tools; the validator **warns** rather than fails, flagging that a new
simulator binding is needed before that record is runnable.

## The verifier contract (why this shape)
The reward in SRE-Degrees is verifiable: an agent's trajectory is graded by
whether it (a) avoids `trap_actions`, (b) executes `canonical_fix.steps` in an
order consistent with `ordering_notes`, and (c) drives the `slo` metric back under
threshold. Encoding these in the ingest record means partner data is *trainable*,
not just readable.

## Validation
```
python3 validate_schema.py incident_ingest_schema.json example_record.json
# -> VALID: partner-cdn-cache-stampede conforms to IncidentRecord v1.0
```
See `example_record.json` for a complete, passing cascade example.
