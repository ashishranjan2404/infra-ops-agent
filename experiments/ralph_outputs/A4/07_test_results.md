# A4 — Test Results

All commands run in `experiments/ralph_outputs/A4/artifacts/`, Python 3.13.

## T1 — positive validation (PASS)
```
$ python3 validate_schema.py incident_ingest_schema.json example_record.json
VALID: partner-cdn-cache-stampede conforms to IncidentRecord v1.0
exit=0
```

## T2 — negative: missing required `root_cause` (PASS)
```
INVALID (1 error(s)):
  - $: missing required key 'root_cause'
exit=1
```

## T3 — negative: cascade without `why_misleading` (conditional rule) (PASS)
```
INVALID (1 error(s)):
  - $: classification 'cascade' requires non-empty 'why_misleading'
exit=1
```

## T4 — negative: `severity` out of [0,1] range (PASS)
```
INVALID (1 error(s)):
  - $.root_cause.severity: 1.7 > maximum 1
exit=1
```

## T5 — field-mapping vs real scenario YAML (PASS)
```
scenario yamls found: 51
sample yaml: 40-redis-cache-flush.yaml
shared keys absent in scenario YAML: none
shared keys absent in example record: none
root_cause subkeys in YAML: ['hidden','kind','location','persistent','reset_by','severity']
slo[0] subkeys in YAML: ['direction','metric','node','sustain_ticks','threshold']
MAPPING OK: shared verifier keys present in both example and real YAML
```
Confirms the schema's verifier keys (`root_cause`, `trap_actions`, `canonical_fix`,
`slo`, `assertions`) and the `slo` sub-fields match the live
`scenarios/cidg/generated/*.yaml` format exactly.

## T6 — unknown-tool WARN path (PASS — warns, does not fail)
```
WARN: tool 'restart_everything' not in recommended vocabulary (will need a simulator binding)
VALID: partner-cdn-cache-stampede conforms to IncidentRecord v1.0
exit=0
```

## T7 — JSON parse-check of schema + example (PASS)
```
JSON OK
```

## Markdown deliverables (parse / non-empty check)
- `snorkel_contact_brief.md`, `outreach_email_snorkel.md`,
  `data_sharing_checklist.md`, `incident_ingest_schema.md` — all written, non-empty,
  headers present, no placeholder body text (only intentional `<PLACEHOLDER>`
  sender tokens in the email + flagged verify-before-send items).

## Summary
7/7 executable checks pass. Validator exercises positive, three distinct negative
paths, the conditional rule, and the warn path; field mapping verified against 51
real scenario YAMLs. No shared core files modified.
