# incident.io — outreach draft

**To:** `[VERIFY]` incident.io DevRel / partnerships
**Subject:** Your anetd postmortem is already a benchmark scenario — can we credit you + go deeper?

Hi incident.io team,

I'm a researcher on SRE-Degrees, an open benchmark that trains and evaluates agents on realistic
incident-response scenarios. Your public postmortems are clear enough that we faithfully
reconstructed one of your incidents (the anetd CPU / network-agent saturation event) as a
reusable scenario in our open set — credit to your transparency. We'd love your eyes on how
you're represented, and we'd be glad to cite that you reviewed it.

A company whose whole product is incident learning is the natural home for a public incident
*benchmark*. Two small asks, either is a win:

1. A 20-minute call to walk you through how the benchmark works and how you're represented.
2. (Optional) Sharing the structured internals your blog strips out — an anonymized timeline
   (offsets only), the *shapes* of the alerts that fired (signal + threshold relation + unit, no
   values), and the remediation steps — for incidents you've already disclosed publicly. The
   exact JSON shape and our anonymization handling are in the attached spec; v1 only ever touches
   already-public incidents, and we're happy to sign your DPA for anything beyond that.

Worst case, a "you may cite that we reviewed our representation" is still hugely useful to us.

Thanks for building in the open,
<Researcher Name / SRE-Degrees project>
*(attach: anonymization_spec.md, anonymization_schema.json)*

---
**Short DM / LinkedIn variant (≤60 words):**
Hi — researcher on SRE-Degrees (open incident-response benchmark). Your anetd postmortem was so
clear we rebuilt it as a benchmark scenario, with credit. Could we get 20 min to show how you're
represented, and ask about optionally sharing the anonymized timeline/alert-shapes your blog
strips out? Spec + anonymization details ready. Even a "you may cite our review" helps.
