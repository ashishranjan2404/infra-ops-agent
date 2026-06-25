# incident.io — positioning + contact brief

**Identity:** Incident management platform (declare, coordinate, post-incident learning). Their
product *is* incident data tooling — this is our highest-probability partner.

## Warm hook
We already model one of their public reliability incidents:
- `scenarios/cidg/generated/52-incidentio-anetd-cpu.yaml` — incident.io anetd CPU incident
  (cilium/networking-class failure).

Open by crediting their transparency and noting that a company whose product is incident
learning is the natural home for a public incident *benchmark*.

## What we are already permitted to do (provenance)
Their postmortem is publicly published. We model the failure mechanism (anetd CPU / network
agent saturation), cite the source, and use no proprietary data.

## Why they'd say yes (strongest of the three)
- **Direct marketing value:** an open SRE-incident benchmark that their product could top is
  category-defining content for them.
- **Mission fit:** they evangelize good post-incident practice; contributing structured,
  anonymized incident internals to research is on-brand.
- **DevRel-forward:** active engineering blog and conference presence; receptive to research
  collaborations.

## The ask (least-sensitive useful slice)
Anonymized *structured internals* of incidents they've already publicly disclosed — timeline
(offsets), alert *shapes*, remediation steps — in `anonymization_schema.json` form. **Stretch
(clearly optional):** because incident management is their domain, ask whether they'd
co-design an export from their own platform's anonymized post-incident data (aggregated, no
customer content) — a genuine research collaboration.

## Contact path (role-based / public only — VERIFY before sending)
- `[VERIFY]` incident.io DevRel / Developer Advocacy public channel.
- `[VERIFY]` Engineering blog author bylines (incident.io/blog) — approach the team.
- `[VERIFY]` Their public "contact"/partnerships form on incident.io.
- `[VERIFY]` Founders/eng-leads are publicly active (conference talks) — engage via *public*
  professional handles only; no scraped private email.

## Objection handling
- *"Customer data risk?"* → We only want already-public incidents in v1; the stretch ask is
  aggregated/anonymized, and we'll sign a DPA.
- *"What's in it for us?"* → A public benchmark in your category + research co-citation.
- *"Effort?"* → Minimal: bless our representation, or export a handful into our JSON shape.

## Yield estimate & fallback
**Probability: HIGH (relative).** **Fallback:** if no data, secure a public quote / blessed
representation + permission to cite — still a strong outcome given the marketing alignment.
