# A3 — Summary

**Task:** Source 10+ fully real (first-party, not public-postmortem-derived) incidents via company outreach.

**Outcome:** Delivered the complete, validated outreach + intake machinery. The actual sending of outreach and signing of data-use agreements are human/legal actions an autonomous agent cannot perform, so no incidents are yet in hand — honestly documented as the blocker. All 10 step files written.

## Real artifacts (experiments/ralph_outputs/A3/artifacts/)
- target_companies.md — 16 targets, two tracks (community_warm / dua_nonpublic), rationale + reachability + expected provenance; funnel to reach 10+.
- outreach_templates.md — 4 sendable templates (cold email, warm intro, community DM, public call-for-contributions), anonymization- and reciprocity-first.
- intake_schema.json — draft-07 schema; required root_cause/trap_action, required consent object, provenance enum; maps 1:1 to opensre-traj/specs/real/*.json.
- intake_example.json — worked de-identified non-public incident that validates and shows the cascade shape (victim alert != cause; trap action; correct fix).
- consent_anonymization.md — consent tiers, 1-page DUA term sheet, de-identification checklist, provenance defensibility.
- tracking_sheet.csv — 16-row campaign tracker with enforced status/track enums.
- validate.py — T1-T4 all PASS (schema validate, negative test, CSV parse, category check); ran via real jsonschema Draft7.

## Verification
python3 .../validate.py -> ALL CHECKS PASSED (exit 0). No shared core files edited.

## Key honesty
The deliverable is machinery + one worked example, not 10 obtained incidents. The novelty claim ("fully real / non-public") is enabled by the provenance enum + DUA track but is only illustrated, not yet evidenced by real donor yield. Next step: build the intake -> specs/real transform + evidence-author scaffold.
