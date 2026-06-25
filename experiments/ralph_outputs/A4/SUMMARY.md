# A4 — Summary: Reach out to Snorkel for incident logs

## Task
Action item A4 (`NEXT_100_TASKS.md`) / #14 (`ACTION_ITEMS.md`): reach out to
Snorkel AI (an RL-data company referenced in the paper) for incident data.

## What was delivered (real artifacts)
A complete, send-ready outreach package + a tested ingest schema, all under
`experiments/ralph_outputs/A4/artifacts/`:
1. **snorkel_contact_brief.md** — researched contact & positioning brief (Snorkel
   RL gyms, verifiable rewards, $3M Open Benchmarks Grants; real channels only;
   Armin Parchami as target persona; honest evidence-class section).
2. **outreach_email_snorkel.md** — tailored email (collaboration framing, tiered
   ask, 30-min CTA) + short warm-intro variant.
3. **data_sharing_checklist.md** — 7-phase NDA / anonymization / PII / license /
   security / retention / publication gating list.
4. **incident_ingest_schema.json + .md** — IncidentRecord contract capturing the
   verifier semantics, a superset of the real scenarios/cidg/generated/*.yaml
   format; with example_record.json and a stdlib validate_schema.py.

## Verification
7/7 executable checks pass: positive validation, 3 negative paths (missing-
required, cascade-conditional, range), unknown-tool warn, JSON parse, and a
field-mapping check proving the schema's verifier keys match 51 real scenario
YAMLs exactly.

## Honest status
Completed deliverable, outcome pending. No email was sent and no data obtained —
an offline worker cannot send mail or land a reply; that is out of scope and
documented. Partner data, if obtained, would address the self-authoring/
contamination critique but would NOT close the "0 fully real raw incidents" gap
(INCIDENT_DATASET.md); the brief states this plainly. No shared core files were
edited; the partner->YAML converter is specified, not built (parallel-safety).
