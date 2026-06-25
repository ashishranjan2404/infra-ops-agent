# A4 — Verification against success criteria

| Success criterion (from 01/03) | Met? | Evidence |
|---|---|---|
| Contact & positioning brief, real channels only | ✅ | `snorkel_contact_brief.md`; channels confirmed via research (partners/contact pages, LinkedIn); Parchami named as persona with "do not fabricate email" |
| Tailored outreach email draft | ✅ | `outreach_email_snorkel.md` — full email + short variant, collaboration + tiered ask + 30-min CTA |
| Data-sharing / legal checklist | ✅ | `data_sharing_checklist.md` — 7 gating phases |
| Proposed ingest data schema | ✅ | `incident_ingest_schema.json` + `.md` + passing `example_record.json` |
| Schema validates against its own example (exit 0) | ✅ | T1 exit 0 |
| Schema maps onto real scenario YAML | ✅ | T5 — shared keys present in both, across 51 YAMLs |
| Explicit evidence-class honesty + "sending out of scope" | ✅ | brief §5 + §6; checklist Phase 6 |
| No shared core files edited | ✅ | only wrote under `experiments/ralph_outputs/A4/`; proposed converter documented, not created |

## Are the outputs real (not placeholder)?
- **Brief:** grounded in *researched* Snorkel facts (RL-gym domains, verifiable
  rewards, $3M Open Benchmarks Grants, Series D), not generic filler. Real.
- **Email:** specific to our 19-incident corpus and Snorkel's framing; only the
  sender identity is a deliberate `<PLACEHOLDER>` (we must not invent a person).
  Real, send-ready after filling identity + verifying the form URL.
- **Checklist:** concrete, actionable items, not boilerplate. Real.
- **Schema + validator + example:** executable; 7/7 tests pass including negative
  paths and a real-YAML field-mapping check. Real and runnable.

## Honest limits (carried to 09)
- Cannot send the email or confirm Parchami's current role/contact — out of scope
  and time-sensitive; flagged for human verify-before-send.
- The schema's value is realized only once a `partner→YAML` converter exists; that
  converter is intentionally NOT built (parallel-safety) but is fully specified.
