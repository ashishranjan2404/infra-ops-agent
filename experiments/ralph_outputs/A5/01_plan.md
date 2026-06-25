# 01_plan — A5: Outreach to CircleCI, incident.io, Cloudflare for anonymized incident data

## Objective
Produce REAL, send-ready outreach assets to obtain **anonymized incident / postmortem data**
from three target companies — CircleCI, incident.io, Cloudflare — for the SRE-Degrees RL
research project (code-as-policy auto-harness over simulated incidents). Actual *sending* is
explicitly out of scope (no verified channels, no authority to bind the project legally). The
deliverable is the complete outreach package a human can review and send.

## Why these three
Each already has **public postmortems** that we have ingested into `scenarios/cidg/generated/`:
- CircleCI — `50-circleci-kubeproxy-iptables.yaml` (1 scenario)
- incident.io — `52-incidentio-anetd-cpu.yaml` (1 scenario)
- Cloudflare — `58/59/60/71/76-cloudflare-*.yaml` (5 scenarios)

This is the single strongest hook: we are not cold-asking for secret data — we already
respectfully model their *public* incidents, and we are asking whether they'll share
*additional anonymized* signal (timelines, alert payloads, remediation steps) that public
blog posts strip out. Each company also has a distinct strategic reason to say yes:
- **incident.io** sells incident management — research credibility + a benchmark their product
  could top is direct marketing value.
- **Cloudflare** has a strong public-postmortem culture and a research/academic outreach habit.
- **CircleCI** is a CI/CD vendor whose 2023 security incident made transparency a brand priority.

## Approach (artifacts to create)
1. **Per-company positioning + contact brief** (`artifacts/briefs/<company>.md`) — who they are,
   why they'd care, the specific ask, the realistic contact path, objection-handling, and the
   public incident(s) we already use as the warm hook.
2. **Tailored outreach drafts** (`artifacts/outreach/<company>_email.md` + a short
   LinkedIn/DM variant) — each genuinely tailored, not template-filled.
3. **Anonymization spec** (`artifacts/anonymization_spec.md`) — the exact contract we offer:
   what fields we want, what we strip, k-anonymity / redaction rules, retention, and a
   machine-readable schema so a partner engineer can self-serve.
4. **Tracking sheet** (`artifacts/tracking.csv`) — CRM-style row per company/contact with
   status, channel, last-touch, next-action.
5. A tiny **validator** (`artifacts/validate.py`) that parses the CSV + the anonymization
   schema (JSON) so the package is provably well-formed.

## Files to create / modify
- Create only under `experiments/ralph_outputs/A5/` — NO shared-core edits.
- Read-only reference: `scenarios/cidg/generated/*cloudflare*.yaml`, `*circleci*.yaml`,
  `*incidentio*.yaml` for the warm-hook citations.

## Dependencies
- None external. Pure docs + a stdlib-only Python validator. Python 3.13.

## Risks
- **Fabricated contacts** — I must NOT invent personal emails. Mitigation: use *role-based /
  publicly-documented* channels only (e.g. security@, press@, public research-contact forms,
  named public DevRel/SRE figures with their public-facing handles only) and clearly flag every
  contact as "verify before sending."
- **Legal overreach** — promising anonymity guarantees we can't keep. Mitigation: the
  anonymization spec is an *offer of our handling*, plus a "we'll sign your DPA/NDA" line.
- **Out-of-scope creep** — actually emailing. Mitigation: explicit "DO NOT SEND yet" banner.

## Success criteria
- 3 distinct, non-templated positioning briefs with a real warm hook each.
- 3 tailored email drafts + short variants that a human could send after a 5-min review.
- An anonymization spec with a parseable JSON schema + redaction rules.
- A tracking CSV that the validator parses green.
- Honest blocker documented: sending + any private contact discovery is out of scope.
