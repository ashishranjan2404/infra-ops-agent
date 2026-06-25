# A11 — 04 Spec

## Scenario YAML schema (matches existing `scenarios/cidg/generated/*.yaml`)
Top-level keys (all required): `meta, topology, root_cause, fault, observation,
slo, trap_actions, canonical_fix, assertions, chance, seed`.

- `meta`: `{id, title, source, urls:[], failure_class, clouds:[gke,lke]}`
- `topology`: `{nodes:[{name, kind, resources:{replicas:int}}], edges:[{from,to,
  type, weight, latency_add_ms?, retry?}]}`
- `root_cause`: `{location, kind(=failure_class), severity:0.7, hidden:bool,
  persistent:false, reset_by:[]}`
- `fault`: `{chaos_kind:exec, exec_cmd, sim:{set:{"<class>_active":true}}, duration_s:120}`
- `observation`: `{alerting:uniform, monitoring_degrades:false, smoking_guns:[{tool,
  node, signature, buried_under}]}`
- `slo`: list of `{metric:error_rate_pct, node, direction:higher_bad, threshold:5,
  sustain_ticks:3}`
- `trap_actions`: list of `{tool, args}`
- `canonical_fix`: `{ordering_notes, steps:[{tool, args:{target,...}}]}`
- `assertions`: `{cascades, loudest_alert_not_cause, fix_resolves:true,
  buried_gun_exists, hysteresis:false, monitoring_degrades:false}`
- `chance`: `{flap_prob:0.05, jitter:0.03, partial_recovery_prob:0.0}`
- `seed`: int

## "Root cause" invariant (held within a pair)
`meta.failure_class == root_cause.kind == fault.sim.set key prefix`, and
`canonical_fix.steps[0].tool`. Both must be EQUAL across A and B in a pair.

## "Surface symptom" variables (varied within a pair)
topology node count/names/kinds, edges, `slo[].node`, `observation.smoking_guns`,
`assertions.cascades / loudest_alert_not_cause / buried_gun_exists`,
`trap_actions[].args.target`, seed.

## The 3 pairs
| pair | failure_class | fix tool | A (leaf) | B (cascade) |
|------|---------------|----------|----------|-------------|
| P1 | fd_exhaust | restart_service | log-shipper self-errors | api-gw socket exhaustion → orders-svc + notify-svc breach |
| P2 | cert_expire | renew_certificate | payments-svc mTLS rejects | tls-ingress cert → web-frontend + mobile-bff 5xx |
| P3 | mem_leak | increase_memory_limit | transcoder OOMs | object-cache leak → catalog-api + recsys degrade |

## `pairs_manifest.json` contract
```json
{
  "description": "...",
  "generated_dir": "scenarios/cidg/generated/",
  "pairs": [
    {"pair_id":"P1",
     "shared_root_cause":{"failure_class":"fd_exhaust","fix_tool":"restart_service"},
     "A":"80-fd-exhaust-leaf-shipper.yaml",
     "B":"81-fd-exhaust-cascade-gw.yaml",
     "symptom_A":"...","symptom_B":"..."}
  ],
  "files":["80-...yaml", ...]
}
```

## Generator function signatures (`make_pairs.py`)
- `leaf_node(name, kind="service", replicas=2) -> dict`
- `scenario(*, sid, title, failure_class, nodes, edges, root_loc, root_hidden,
  smoking_guns, slo, trap_actions, fix_tool, fix_args, cascades,
  loudest_not_cause, buried_gun, seed) -> dict`
- `main()`: refuse-if-exists guard → write+roundtrip-parse each YAML → assert pair
  invariants → write manifest (to generated/ and to artifacts/).

## Test cases
1. Each YAML parses with `yaml.safe_load` and round-trips its fix tool + class.
2. Key set of each new YAML ⊇ required top-level keys.
3. For each pair: `fc(A)==fc(B)` and `tool(A)==tool(B)` and `len(nodes A)!=len(nodes B)`.
4. No filename collision with the 40-79 existing set.
5. Manifest parses and has 3 pairs / 6 files.
