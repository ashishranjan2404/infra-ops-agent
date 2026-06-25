# A3 — Source 10+ fully real incidents (company outreach) — Plan

## Objective
Stand up a **repeatable outreach + intake pipeline** to source **10+ fully real,
first-party incidents** — i.e. incidents donated directly by companies/practitioners
*as raw artifacts* (alert timelines, chat/incident-channel transcripts, runbook steps
taken, postmortem drafts), NOT incidents we synthesized from already-public postmortems.

This is the key distinction vs the existing corpus:
- `opensre-traj/specs/real/*.json` (19 entries) and `real-incidents/catalog.md` are
  **derived from public postmortems** — real events, but second-hand and already public.
- A3 wants **net-new, donated, possibly non-public** incident material that we control the
  raw fidelity of (the loud-symptom alert text, the actual trap action taken, the timeline).

Because an autonomous agent **cannot actually send cold emails, sign data-use agreements,
or get a human on a call**, the honest deliverable is the *full machinery* to execute the
outreach: a prioritized target list with rationale, ready-to-send email/DM templates, a
structured data-intake schema (so a donated incident maps 1:1 into our spec format), a
de-identification/anonymization checklist, and a tracking sheet to run the campaign.

## Approach
1. Build a **target list** (companies + communities + individuals) with rationale and a
   warm/cold-path classification — who is reachable, who has a public incident culture,
   who already publishes postmortems (= culturally willing to share).
2. Write **outreach templates** for each channel: cold email, warm intro, conference/Slack
   DM, and a "donate an incident" public call-for-contributions.
3. Define a **data-intake schema** (YAML/JSON) that mirrors `specs/real/*.json` so any
   donated incident drops straight into the pipeline, plus a **consent + anonymization**
   form so legal/privacy is handled.
4. Provide a **tracking sheet** (CSV) to run the campaign: status per target, owner,
   follow-up dates.
5. Validate all artifacts: CSV parses, JSON-schema is valid JSON, templates render.

## Files to create (all under A3/artifacts/)
- `target_companies.md` — prioritized list + rationale + reachability tier
- `outreach_templates.md` — 4 templates (cold email, warm intro, community DM, public CFC)
- `intake_schema.json` — JSON Schema for a donated incident (maps to specs/real format)
- `intake_example.json` — one worked example showing a donated incident filled in
- `consent_anonymization.md` — data-use consent + de-identification checklist
- `tracking_sheet.csv` — campaign tracker
- `validate.py` — checks CSV parses, JSON valid against schema, example validates

## Dependencies
- Python 3.13 stdlib only (csv, json). Optional `jsonschema` for strict validation; fall
  back to a hand-rolled check if not installed (no network/pip assumed).
- No live cluster, no external API needed.

## Risks
- Cannot actually execute outreach (send mail / get signatures) — autonomous blocker.
- Donated data has legal/privacy weight; templates must be conservative and consent-first.
- "Fully real, non-public" incidents are the hardest to get — most willing donors will
  give *already-public* material, so the schema must accept both and tag provenance.

## Success criteria
- A prioritized list of **>= 15 targets** (to realistically yield 10+ incidents).
- >= 4 channel-specific outreach templates, each self-contained and sendable.
- A valid intake schema that maps 1:1 onto our existing `specs/real/*.json` fields, with a
  worked example that passes validation.
- A consent/anonymization checklist.
- A parsing-valid tracking CSV.
- `validate.py` runs green.
