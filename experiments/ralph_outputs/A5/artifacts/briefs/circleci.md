# CircleCI — positioning + contact brief

**Identity:** Cloud CI/CD platform. Strong public-engineering-blog culture; post-2023 made
transparency a brand priority.

## Warm hook
We already faithfully model one of their public reliability incidents as a benchmark scenario:
- `scenarios/cidg/generated/50-circleci-kubeproxy-iptables.yaml` — "CircleCI 2023-03-14
  kube-proxy iptables-restore outage" (failure_class: net_delay, GKE/LKE topology).

The opening line credits their transparency: their public postmortem was clear enough that we
could reconstruct the *failure mechanism* as a reusable RL benchmark.

## What we are already permitted to do (provenance)
The 2023-03-14 postmortem is publicly published by CircleCI. We cite the source and model the
*failure mechanism* (control-plane net delay via kube-proxy), not any proprietary data. No
private data is used. This brief is about *additional, optional* anonymized signal.

## Why they'd say yes
- Reliability research that uses their *public* incident as a positive example is good PR.
- A standing benchmark that includes their incident class signals engineering maturity.

## The ask (least-sensitive useful slice)
The **structured internals their public blog stripped out** of incidents they have *already
disclosed*: an anonymized timeline (offsets, not wall-clock), the *shapes* of the alerts that
fired (signal name + threshold relation + unit, no values), and the ordered remediation steps —
in the JSON shape in `anonymization_schema.json`. Explicitly scoped to **operational /
reliability** incidents. **We are not asking about the 2023 security breach.**

## Contact path (role-based / public only — VERIFY before sending)
- `[VERIFY]` CircleCI Engineering Blog / DevRel public contact (via their public blog "contact"
  / engineering-careers channel).
- `[VERIFY]` Public SRE/Infra engineering author bylines on circleci.com/blog — approach the
  *team*, not a scraped personal address.
- `[VERIFY]` press@ / general public contact form as a last resort.
- DO NOT invent or use any personal/private email. All channels above must be confirmed.

## Objection handling
- *"Is this about the breach?"* → No — strictly reliability/operational incidents you've already
  publicly disclosed; we'll put that in writing.
- *"What do we have to do?"* → Optionally export a few already-public incidents into our JSON
  shape; or just review and bless how we represent your public incident.
- *"Legal?"* → v1 covers only already-public incidents; happy to sign your DPA/NDA for anything
  beyond that.

## Yield estimate & fallback
**Probability: LOW.** Post-breach inbox is cautious. **Fallback:** continue using the public
postmortem we already model (permitted), and ask only for a citable "they reviewed our
representation" — a tiny yes that still strengthens provenance.
