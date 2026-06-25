# 09_critique — honest critical evaluation

## What's weak
1. **Zero verified human contacts.** Every channel is role-based + `[VERIFY]`. A reviewer can
   fairly say "this is a template package, not an outreach campaign." True — by design, because
   inventing contacts would be worse. But it means the *real* gating step (finding the right
   person at each company) is untouched and pushed to a human.
2. **Outcome is speculative.** Probabilities (high/med/low) are my estimates with no base-rate
   data. The honest expected yield across all three is plausibly *zero data records*; incident.io
   is the only one with a self-interested reason to engage.
3. **The ask may still be too big.** Even "structured internals of already-public incidents"
   asks a company to do unpaid work re-exporting data into our schema. The realistic yes is the
   *tiny* CTA (review + cite permission), and even that competes for busy DevRel attention.
4. **Anonymization spec is an offer, not a guarantee.** R2/R3 (no infra IDs / no people) are a
   human+regex pipeline I described but did not implement here — a partner lawyer could push for
   a tested, auditable redactor before sharing anything. We'd need real code for phase-2.
5. **Email length over the self-imposed target.** Minor, documented, but a stricter reviewer
   would want a tighter 150-word version per company.

## What a reviewer attacks first
- "You never contacted anyone." Correct — sending is out of scope; this is the prep artifact.
- "Probabilities are made up." Correct — labeled as estimates in the CSV/banner.
- "Ethics: did you have the right to model these postmortems?" Answered in each brief's
  provenance section (public sources, failure-mechanism only), but not as a signed agreement.

## What's missing
- A real, tested redaction script (only specified, not built).
- A 150-word ultra-short email variant.
- Any base-rate/precedent research on how these specific DevRel teams respond to research asks.

## Honest status
**Completed deliverable, blocked downstream.** The outreach package is real, well-formed, and
validator-green. Actual sending, verified contact discovery, and any data acquisition are
out of scope / blocked — and I did not fake any of them. incident.io is the recommended first
real send; CircleCI and Cloudflare should lead with the tiny review-and-cite CTA.
