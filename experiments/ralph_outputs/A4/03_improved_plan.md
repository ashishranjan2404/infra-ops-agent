# A4 — Improved Plan (post-grill)

## What changed vs 01_plan.md

| Change | Driver | Accept/Reject |
|---|---|---|
| Reframe ask from "incident logs" → **co-built open SRE/incident RL benchmark** | SMR, RLE | **Accepted** |
| Add an explicit **tiered ask**: moonshot (open benchmark / runnable gym) + fallback (a few NDA'd structured records to validate schema) | PSRE, SMR | **Accepted** |
| Email leads with substance + a 30-min CTA; **legal lives in a separate checklist**, not in the cold email | DEVOPS over PSRE | **Accepted** |
| Brief must **explicitly state the evidence class**: this mitigates self-authoring/contamination, it does NOT close the "0 fully real raw incidents" gap | REV | **Accepted** — added a "What this does and does not buy us" section to the brief |
| Schema must encode the **verifier contract** (trap_actions, canonical_fix, SLO assertions), not just prose | RLE | **Accepted** — schema mirrors scenario YAML's `trap_actions`/`canonical_fix`/`slo`/`assertions` |
| Never request raw prod logs; request **anonymized structured records / runnable env** | PSRE, RLE | **Accepted** — wired into email + checklist + schema (`pii_status`, `anonymization` fields) |

## Rejected / deferred
- **REV's implication that Snorkel data is near-worthless** ("all constructed"):
  rejected as an over-correction. We keep the ask but *label* the evidence class
  honestly. RLE's point stands: third-party-authored + verifiable still breaks our
  self-authoring contamination problem, which is a real, citable win.
- **PSRE's "NDA-first" cold email**: rejected. Legal is gating but belongs in the
  internal checklist, surfaced only after mutual interest.

## Final artifact set (unchanged count, sharpened content)
1. `artifacts/snorkel_contact_brief.md` — + "evidence class" honesty section,
   + tiered-ask strategy, only real contact paths.
2. `artifacts/outreach_email_snorkel.md` — collaboration framing, tiered ask,
   substance-forward, short variant, 30-min CTA.
3. `artifacts/data_sharing_checklist.md` — NDA, anonymization, license, PII,
   retention, security review — the gating list.
4. `artifacts/incident_ingest_schema.json` + `.md` — verifier-contract schema
   mapped onto scenario YAML; `artifacts/example_record.json`;
   `artifacts/validate_schema.py` (runnable, stdlib-only).

## Success criteria (sharpened)
- Validator exits 0 on the example; example field names map onto real
  `scenarios/cidg/generated/*.yaml` keys (root_cause, trap_actions, canonical_fix,
  slo, assertions).
- Brief contains an explicit honesty paragraph on evidence class + "sending is out
  of scope."
