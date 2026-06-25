# 03_improved_plan — revised after the grill

## What changed vs 01
1. **Reframed the ask** (PSRE + SMR synthesis): we no longer ask for raw alert streams. We ask
   for *structured internals of incidents they have already publicly disclosed* — the timeline,
   alert payload shapes, and remediation steps that the public blog post strips out. Lowest
   sensitivity, highest reply probability. The warm hook ("we already model your public
   postmortem in `cidg`") becomes the opening line of every email, not a footnote.
2. **Anonymization spec placement** (REV vs RLE resolved): the spec *exists* as a formal,
   citable artifact with a JSON schema and redaction rules (REV), but the email body carries
   only a one-paragraph plain-English promise and references the attachment (RLE).
3. **Honest yield ranking added** (DOL): each brief now ranks realistic probability and states
   the fallback (keep using public postmortems — already permitted). Order: incident.io (high) >
   Cloudflare (medium) > CircleCI (lower).
4. **Format-first ask** (RLE): the email and spec both specify the machine-friendly shape
   (JSON timeline + alert payload shapes) so a partner engineer can self-serve.
5. **Tracking sheet promoted to primary success metric** (DOL): success = warm thread open, not
   data in hand.

## Critiques accepted
- PSRE "ask for the least-sensitive slice" — ACCEPTED, reshaped the entire ask.
- DOL "be honest about low yield / add fallback" — ACCEPTED, added per-brief probability+fallback.
- RLE "format-first / machine-friendly" — ACCEPTED, baked into spec + email.
- REV "citable formal protocol must exist" — ACCEPTED as an attachment.

## Critiques rejected (with reason)
- SMR "raw anonymized alert streams are the prize" — REJECTED as the *ask*. Correct about
  research value but PSRE + DOL are right that it has ~0% yield and leaks customer/topology data;
  pursuing it poisons the relationship. Kept as a *stretch* item only, explicitly labeled.
- RLE "spec as appendix-only, keep it light" taken to the extreme — PARTIALLY REJECTED. The spec
  must be formal enough to cite in a paper (REV). Compromise: formal artifact, light email.

## Final deliverable list
- `artifacts/briefs/{circleci,incidentio,cloudflare}.md` — positioning + contact brief each,
  with warm hook, ask, contact path (role-based only), objections, yield estimate, fallback.
- `artifacts/outreach/{circleci,incidentio,cloudflare}_email.md` — tailored email + short DM.
- `artifacts/anonymization_spec.md` + `artifacts/anonymization_schema.json` — the offer.
- `artifacts/tracking.csv` — CRM rows.
- `artifacts/validate.py` — parses CSV + JSON schema, asserts well-formedness.
- `DO_NOT_SEND.md` banner — sending is out of scope; verify contacts before any send.
