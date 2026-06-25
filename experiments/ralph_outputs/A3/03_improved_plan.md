# A3 — Improved Plan (post-grill)

## What changed vs 01_plan.md
1. **Added `provenance` enum** to the intake schema (`public_postmortem` |
   `first_party_donated` | `first_party_nonpublic`). *Accepted* RLE+AAAI: cheap, resolves the
   "is this actually novel vs the 19 public ones?" reviewer attack by letting us filter the
   genuinely first-party / non-public subset.
2. **Short intake form, but `root_cause` and `trap_action` required free-text.** *Accepted*
   the SMR/PSRE compromise: heavy structured forms kill donor response; but the one thing
   only a first-party donor can give us — what the trap was and the true root cause — stays
   mandatory.
3. **Anonymization-first, reciprocity-first templates.** *Accepted* PSRE: narrow,
   de-identified ask + offer the finished graded scenario back as the incentive.
4. **Two-track target list.** *Accepted* AAAI/DOL: a `community/warm` volume track and a
   smaller `dua_nonpublic` track, each row tagged with reachability + expected provenance.
5. **Framed as a human-run runbook + machinery, not auto-executed.** *Accepted* DOL/AAAI:
   the agent cannot send mail / sign DUAs; honest blocker documented.

## What I rejected and why
- **SMR's heavy 12-field structured labeling form — REJECTED.** PSRE is right that it kills
  response rate, which is the binding constraint. Kept only 2 required free-text fields.
- **DOL's "communities are enough, skip DUAs" — REJECTED as the whole story.** AAAI is right
  that community donations skew toward already-public material and don't carry the novelty
  claim. Kept the DUA track even though it's slower/human-gated.
- **"Just ship breadth and label later" (pure DOL) — PARTIALLY REJECTED.** We keep required
  ground-truth fields so we don't silently reduce to the public-postmortem pipeline.

## Final deliverables (A3/artifacts/)
- `target_companies.md` — >=15 targets, two tracks, rationale + reachability + expected
  provenance per row.
- `outreach_templates.md` — cold email, warm intro, community DM, public call-for-contrib.
- `intake_schema.json` — JSON Schema mapping 1:1 to `specs/real/*.json` + `provenance`.
- `intake_example.json` — worked donated incident that validates.
- `consent_anonymization.md` — DUA-lite consent + de-identification checklist.
- `tracking_sheet.csv` — campaign tracker with status enum.
- `validate.py` — CSV parse + JSON-Schema validation (stdlib fallback if no jsonschema).

## Success criteria (unchanged + sharpened)
- >=15 targets across two tracks; >=4 templates; schema validates the example; CSV parses;
  `validate.py` exits 0. Provenance is filterable.
