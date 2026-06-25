# A5 — SUMMARY

**Task:** Reach out to CircleCI, incident.io, Cloudflare for anonymized incident data.

**Outcome:** Completed deliverable (review-ready outreach package); actual sending + contact
discovery + data acquisition are out of scope / blocked and were NOT faked.

## Deliverables (all under experiments/ralph_outputs/A5/artifacts/)
- Per-company briefs: briefs/{circleci,incidentio,cloudflare}.md — positioning, warm hook
  (real cidg scenario), strategic incentive, role-based contact path, objection handling,
  yield estimate + fallback.
- Tailored outreach drafts: outreach/{circleci,incidentio,cloudflare}_email.md — full email
  + <=60-word DM variant each, genuinely tailored.
- Anonymization offer: anonymization_spec.md (rules R1-R5) + anonymization_schema.json
  (JSON Schema draft 2020-12, 7 fields, parseable).
- Tracking sheet: tracking.csv (6 rows / 3 companies).
- Validator: validate.py (stdlib only) -> OK: 3 companies, 6 contact rows, schema fields=7.
- Scope guard: DO_NOT_SEND.md.

## Key facts
- Warm hooks verified to exist: CircleCI 50-*, incident.io 52-*, Cloudflare 58/59/60/71/76-*.
- Yield ranking: incident.io HIGH > Cloudflare MEDIUM > CircleCI LOW; each with a public-postmortem fallback.
- No personal/private contacts invented — all channels role-based and [VERIFY]-tagged.
- No shared-core files modified.

## Tests
All green: validator exit 0, schema parses, 7 cited scenarios exist, no leaked webmail addresses.
Email bodies (231-273w) slightly exceed the soft <=220 target — kept for legal-scope clarity.
