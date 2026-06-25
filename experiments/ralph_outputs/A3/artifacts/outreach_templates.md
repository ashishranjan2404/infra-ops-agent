# Outreach templates

Principles (from grill + ouroboros): **anonymization-first**, **reciprocity-first**, narrow
ask, **donor redacts before sending**, **never published without written OK**. Every template
references `consent_anonymization.md`. **Sending is a human action — the agent only drafts.**

Merge fields: `{{name}}`, `{{company}}`, `{{warm_ref}}`, `{{your_name}}`, `{{project_link}}`.

---

## 1. cold_email
**Subject:** A 10-minute ask: donate one de-identified incident to an open SRE benchmark

Hi {{name}},

I'm building an open research benchmark that teaches AI agents to diagnose *cascading*
production outages — the kind where the loudest alert points at a victim, not the cause, and
the obvious fix makes things worse. We grade on root cause + correct fix + trap-avoidance.

I'd love to include one real incident from {{company}}. The ask is narrow and **de-identified
by you before you send anything**:
- the misleading symptom/alert (text, redacted),
- a short timeline of actions taken (including any fix that made it worse),
- the actual root cause and the fix that worked.

No hostnames, customer data, or security details — you redact, we never publish anything
without your written sign-off. In return you get the finished, graded scenario back as a
reusable training/onboarding artifact. Consent + anonymization details: {{project_link}}.

Happy to do a 15-min call or just take a paragraph by email. Thank you!
{{your_name}}

---

## 2. warm_intro
**Subject:** {{warm_ref}} suggested I reach out — donating an incident to an open benchmark

Hi {{name}},

{{warm_ref}} thought you might be a great fit. I run an open benchmark for AI incident-response
on *cascading* outages (loud victim symptom, a trap fix that backfires, the correct sequence).

Would {{company}} be open to donating **one de-identified incident**? You redact before
sending; we never publish without written OK; you get the graded scenario back. The whole ask
is the alert text, the timeline of actions (incl. anything that worsened it), the real root
cause, and the fix. Details + consent terms: {{project_link}}.

15 minutes whenever suits you — thanks!
{{your_name}}

---

## 3. community_dm  (Slack / Discord / Reddit)
Hey {{name}} 👋 — building an open benchmark that trains AI agents on *cascading* outages
(the loud alert points at the victim, the naive fix makes it worse). Looking for real war
stories: the misleading symptom, the trap action someone took, and the actual root cause +
fix. Fully de-identified — you redact, nothing published without your OK, and you get the
graded scenario back. Open to sharing one? Terms: {{project_link}} 🙏

---

## 4. public_cfc  (Call for Contributions — blog/newsletter/SREcon blurb)
**Call for incidents: help build an open SRE-agent benchmark.**

We're assembling a public benchmark of *cascading* production incidents — where the loudest
alert points at a victim instead of the cause, and the obvious fix makes it worse — to test
and train AI incident-responders on root cause, correct fix, and trap-avoidance.

We're looking for **de-identified, first-party incidents**: the misleading symptom, the
timeline of actions (including any fix that backfired), the true root cause, and the correct
remediation. **You redact everything before submitting; nothing is published without your
written consent**, and contributors get the finished graded scenario back.

Submit via the intake form (schema + consent terms: {{project_link}}). Genuinely non-public
incidents can be donated under a light 1-page data-use agreement — reach out.
