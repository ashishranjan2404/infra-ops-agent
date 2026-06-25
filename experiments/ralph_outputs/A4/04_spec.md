# A4 — Technical Spec

## Deliverable 1: Contact & positioning brief (Markdown)
Sections (fixed): Who Snorkel is · Why them · Researched contact paths (with
source URLs + a verify-before-send flag) · Our positioning & leverage · The
tiered ask · What this buys us / what it does NOT (evidence class) · Out-of-scope
note. No invented emails.

## Deliverable 2: Outreach email draft (Markdown)
Contract:
- `Subject:` ≤ 70 chars, references SRE/incident RL benchmark.
- Body: ≤ ~220 words, one primary ask + one fallback, one link placeholder to the
  schema, 30-min-call CTA, signature block with `<PLACEHOLDER>` tokens for sender
  identity (we don't fabricate a person).
- A `--- SHORT VARIANT ---` of ≤ 90 words for a warm-intro / LinkedIn DM.

## Deliverable 3: Data-sharing / legal checklist (Markdown)
A gating checklist with checkbox items grouped: Mutual interest → NDA →
Anonymization/PII → Licensing & attribution → Security/transfer → Retention/
deletion → Publication rights. Each item is actionable (a yes/no a human resolves).

## Deliverable 4: Incident ingest schema

### 4a. JSON Schema (`incident_ingest_schema.json`, draft-07 style)
Top-level object `IncidentRecord`. Required fields:

```
schema_version            string  (e.g. "1.0")
incident_id               string  (slug, ^[a-z0-9-]+$)
source                    object  { org, kind(postmortem|raw_anon|env|reconstructed),
                                    url?, license, anonymization, pii_status(none|redacted|present) }
title                     string
category                  enum    (network_fault|config_error|saturation|resource_exhaustion|
                                    data|conflict|time|cache_flush|other)
classification            enum    (simple|cascade|novel)
loud_symptom              string
why_misleading            string?     (required if classification==cascade)
root_cause                object  { location, kind, severity(0..1), hidden(bool), persistent(bool) }
causal_chain              array<string>   (>=1 step)
trap_actions              array<object>   { tool, args(object) }        # verifier: must NOT resolve
canonical_fix             object  { steps: array<{tool,args}>, ordering_notes? }  # verifier: resolves
slo                       array<object>   { metric, node, direction(higher_bad|lower_bad),
                                            threshold(number), sustain_ticks(int>=1) }
assertions                object  { cascades, loudest_alert_not_cause, fix_resolves,
                                    buried_gun_exists, hysteresis, monitoring_degrades } (all bool)
```
Optional: `topology`, `observation`, `chance`, `seed`, `notes`.

This deliberately mirrors `scenarios/cidg/generated/*.yaml`
(`root_cause`, `trap_actions`, `canonical_fix`, `slo`, `assertions`) plus the
`catalog.md` fields (`loud_symptom`, `why_misleading`, `causal_chain`, `category`)
and the `INCIDENT_DATASET.md` `classification` taxonomy — so a partner record
normalizes straight into the existing pipeline.

### 4b. Validator (`validate_schema.py`)
- Stdlib only (`json`). Minimal recursive checker: required keys, type checks,
  enum membership, numeric ranges, the conditional `why_misleading` rule,
  non-empty arrays. Exit 0 = valid; non-zero + readable message = invalid.
- CLI: `python3 validate_schema.py incident_ingest_schema.json example_record.json`.

### 4c. Example (`example_record.json`)
One fully-populated record (a plausible cascade incident) that PASSES the
validator and uses tool names consistent with the repo (`scale_deployment`,
`clear_cache`, `rollback_deployment`, etc.).

## Test cases (in 07)
1. `validate_schema.py` on the example → exit 0.
2. Negative test: a mutated record (missing `root_cause`) → non-zero + message.
3. Negative test: cascade record without `why_misleading` → non-zero.
4. Markdown parse-check: every artifact non-empty, headers present.
5. Field-mapping check: example keys ⊆ union(scenario YAML keys, catalog fields).
