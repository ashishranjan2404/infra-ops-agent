# A3 — Verification against success criteria

| Criterion (from 03_improved_plan) | Status | Evidence |
|---|---|---|
| >= 15 targets across two tracks | PASS | `target_companies.md` has 16 (11 community_warm + 5 dua_nonpublic); CSV mirrors 16 rows |
| >= 4 channel-specific outreach templates | PASS | `outreach_templates.md`: cold_email, warm_intro, community_dm, public_cfc |
| Intake schema maps 1:1 to specs/real/*.json | PASS | mapping table in spec + manual check vs spec 03 (07_test_results T-mapping) |
| Worked example validates against schema | PASS | validate.py T1 (Draft7) |
| Validation actually bites (negative test) | PASS | validate.py T2 — missing root_cause rejected |
| Consent/anonymization checklist | PASS | `consent_anonymization.md` (tiers, DUA terms, checklist) |
| Tracking CSV parses, enums valid | PASS | validate.py T3 (16 rows) |
| Provenance is filterable (novelty claim) | PASS | `provenance` enum in schema + per-row in target list + CSV column |

## Are outputs real, not placeholder?
- The schema is a valid draft-07 document that a real validator enforces.
- The example is a complete, coherent, de-identified incident with a genuine cascade shape
  (victim alert ≠ cause; trap action; correct fix), not lorem-ipsum.
- The templates are sendable as-is after merge-field fill.
- The target list names real, reachable communities/companies with concrete rationale.
- The tracker is a working CSV with enforced enums.

## What an autonomous agent could NOT verify (honest)
- That any company will actually respond / donate (requires sending + humans).
- That a DUA is legally sufficient (requires counsel).
These are documented as blockers, not faked. The deliverable — the machinery — is complete
and validated.
