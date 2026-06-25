# 06_implementation — what was built

All artifacts live under `experiments/ralph_outputs/A5/artifacts/`. No shared-core files touched.

## Real artifacts produced
| Artifact | Path | What it is |
|---|---|---|
| CircleCI brief | `artifacts/briefs/circleci.md` | positioning + contact path + objections + yield |
| incident.io brief | `artifacts/briefs/incidentio.md` | (highest-probability target) |
| Cloudflare brief | `artifacts/briefs/cloudflare.md` | (5-scenario warm hook) |
| CircleCI email | `artifacts/outreach/circleci_email.md` | tailored email + ≤60w DM variant |
| incident.io email | `artifacts/outreach/incidentio_email.md` | tailored email + DM variant |
| Cloudflare email | `artifacts/outreach/cloudflare_email.md` | tailored email + DM variant |
| Anonymization spec | `artifacts/anonymization_spec.md` | data-handling contract (R1–R5) |
| Anonymization schema | `artifacts/anonymization_schema.json` | JSON Schema (draft 2020-12), 7 fields |
| Tracking sheet | `artifacts/tracking.csv` | 6 CRM rows, 3 companies |
| Validator | `artifacts/validate.py` | stdlib-only; parses CSV + schema |
| Send banner | `artifacts/DO_NOT_SEND.md` | scope guard |

## Key design decisions (carried from grill + ouroboros)
- **Warm hook is the lead** of every email: each company's *public* postmortem is already a
  `cidg` scenario. Verified all 7 cited scenario files exist on disk (step 07 T3).
- **Ask = least-sensitive slice:** structured internals (timeline offsets, alert *shapes*,
  remediation order) of *already-public* incidents — not raw alert streams.
- **Hook reframed as credit-to-transparency + offer-to-review** (ouroboros P2.1) so it reads as
  homage, not scraping.
- **Tiny low-commitment CTA** ("review our representation / permission to cite") alongside the
  bigger data ask (ouroboros P2.2).
- **CircleCI scoped to reliability, explicitly NOT the 2023 security breach** (ouroboros P2.3).
- **Anonymization: spec is formal + citable but the email carries only a one-paragraph promise**
  (grill REV vs RLE synthesis). Schema honestly states R2/R3 are a pipeline step, not
  schema-enforced (ouroboros P1.1).
- **Honest yield ranking:** incident.io HIGH > Cloudflare MEDIUM > CircleCI LOW, each with a
  fallback (keep using already-permitted public postmortems).

## Honesty / scope
- **Sending is out of scope** and blocked behind `DO_NOT_SEND.md`. No personal/private contact
  addresses were invented — all channels are role-based/public and tagged `[VERIFY]`.
- Contact discovery beyond public role-based channels was not performed (no authority/verified
  directory). Documented as a blocker in 07/09.
