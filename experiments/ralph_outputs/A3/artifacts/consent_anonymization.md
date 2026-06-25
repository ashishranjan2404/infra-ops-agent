# Consent + anonymization checklist (hard gate)

No incident enters the pipeline unless `consent.granted == true`. Every outreach template
links here. **Sending outreach and signing any DUA are human actions** — not automated.

## Consent tiers
1. **Community donation (no DUA).** Donor shares a de-identified incident publicly/by email.
   `consent: {granted:true, anonymized:true, dua:false}`. Publishable in the benchmark with the
   donor's general OK; specific company name only if explicitly permitted (else `anonymized`).
2. **Non-public donation under DUA.** Genuinely unpublished incident under a 1-page data-use
   agreement. `consent: {granted:true, anonymized:true, dua:true}`. `source_company` set to
   `"anonymized"` unless the DUA permits naming; `source_url: null`.

## 1-page DUA — minimum terms (for a lawyer to finalize; not legal advice)
- Scope: one (or N) de-identified incident description(s) only.
- Donor warrants the submission is de-identified (no customer PII, no secrets/credentials,
  no internal hostnames/IPs, no security-sensitive detail).
- Use: included in an open research benchmark for AI incident-response; may be redistributed
  as part of the dataset.
- No publication of the donor's identity without separate written consent.
- Revocation: donor may request removal of their incident within a stated window.

## De-identification checklist (donor runs BEFORE sending)
- [ ] Remove customer/account names and IDs.
- [ ] Replace real hostnames, IPs, cluster/namespace names with placeholders.
- [ ] Remove credentials, tokens, internal URLs, security-control details.
- [ ] Remove employee names (use roles: "on-call", "infra", "DB owner").
- [ ] Generalize exact timestamps to relative offsets (T+0, T+5m) if precise times are sensitive.
- [ ] Keep the *technical substance*: the misleading symptom, the trap action, the root cause,
      the fix, and the causal chain — these carry the value.

## Reviewer-defensibility (provenance)
Each ingested incident is tagged `provenance`. The "fully real, non-public" novelty claim is
supported only by `first_party_nonpublic` rows under a DUA. `public_postmortem` rows are
accepted but tagged so they can be filtered out of the novelty subset.
