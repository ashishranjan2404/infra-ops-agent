# A4 — Reach out to Snorkel for incident logs — Plan

## Objective
Produce a ready-to-send outreach package to **Snorkel AI** to source real SRE
incident data (raw logs / postmortems / runnable incident environments) for the
SRE-Degrees RL project. The action item (`experiments/NEXT_100_TASKS.md` A4,
`experiments/ACTION_ITEMS.md` #14) says: *"Reach out to Snorkel for incident
logs (RL company, referenced in paper)."*

Sending an email is **out of scope** for an offline Ralph worker (no mailbox,
no human authority to commit a partnership). The deliverable is therefore the
*real artifacts a human needs to press send* — researched, specific, and honest.

## What "done" looks like (real artifacts)
1. **Contact & positioning brief** (`artifacts/snorkel_contact_brief.md`) —
   who Snorkel is, why they're the right ask, the *specific* contact paths that
   actually exist (researched, not invented), and our positioning/leverage.
2. **Tailored outreach email draft** (`artifacts/outreach_email_snorkel.md`) —
   a real email, subject + body, tuned to Snorkel's RL-environments + Open
   Benchmarks Grants framing, with a short variant.
3. **Data-sharing / legal checklist** (`artifacts/data_sharing_checklist.md`) —
   NDA, anonymization, licensing, PII, retention — what must be settled before
   any logs change hands.
4. **Proposed ingest data schema** (`artifacts/incident_ingest_schema.{json,md}`)
   — a JSON Schema for the incident records we'd ingest, mapped onto our existing
   scenario YAML / catalog format so partner data drops straight into the pipeline.
   Plus a worked, validated example record.

## Approach
- Ground the ask in the project's existing incident assets so the request is
  concrete: `experiments/INCIDENT_DATASET.md` (the 0-fully-real gap), the 19-entry
  `opensre-traj/real-incidents/catalog.md`, and the scenario YAML schema in
  `scenarios/cidg/generated/*.yaml`.
- Research Snorkel's *actual* 2025-26 positioning (RL environments, Expert
  Data-as-a-Service, the $3M Open Benchmarks Grants, research-collaboration track)
  so the email speaks their language and proposes a mutually useful artifact
  (an open SRE/incident RL benchmark) rather than begging for free data.
- Design the ingest schema as a superset of our current scenario fields so any
  partner contribution is normalizable, and validate it with a real Python check.

## Files to create
- `experiments/ralph_outputs/A4/01..10*.md`, `SUMMARY.md`, `result.json`
- `experiments/ralph_outputs/A4/artifacts/` (4 deliverables + validator + example)

## Dependencies
- `python3` + stdlib `json` for schema validation (no `jsonschema` needed; I'll
  write a minimal validator so it runs on a bare env). Optional `pyyaml` (already
  in repo deps) to cross-check the example maps onto scenario YAML.

## Risks
- **Inventing contacts.** Mitigation: only cite contact paths confirmed by
  research (snorkel.ai/partners, /contact/, experts portal); flag the rest as
  "verify before send."
- **Over-claiming a partnership.** Mitigation: email asks for a scoped pilot /
  exploratory call, not a signed data deal; legal checklist is gating.
- **Schema drift from real scenario format.** Mitigation: validate example maps
  onto the actual `scenarios/cidg/generated` field names.

## Success criteria
- All 4 artifacts exist, are non-placeholder, and are internally consistent.
- The schema validates against its own example via a runnable script (exit 0).
- Contact brief cites only researched, real contact channels; honest about what
  can't be confirmed and that sending is out of scope.
