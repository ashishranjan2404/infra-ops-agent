# CircleCI — outreach draft

**To:** `[VERIFY]` CircleCI Engineering Blog / DevRel
**Subject:** Your kube-proxy outage postmortem is a benchmark scenario — review it with us?

Hi CircleCI engineering team,

I'm a researcher on SRE-Degrees, an open benchmark for training and evaluating incident-response
agents. Your 2023-03-14 kube-proxy iptables-restore postmortem was clear enough that we
reconstructed its failure mechanism (control-plane network delay) as a reusable benchmark
scenario in our open set — credit to your transparency. We'd value your review of how you're
represented.

To be upfront: this is strictly about **operational / reliability** incidents you've already
disclosed publicly. We are **not** asking about the 2023 security incident.

Two small asks, either is a win:

1. A short review (call or async) of our representation, with permission to cite that you
   reviewed it.
2. (Optional) The structured internals your blog strips out for already-public reliability
   incidents — anonymized timeline offsets, alert *shapes* (signal + threshold relation + unit,
   no values), and remediation steps — in the JSON shape in the attached spec. v1 only ever
   touches already-public incidents; we'll sign your DPA for anything beyond.

Even a "you may cite that we reviewed our representation" would help us a lot.

Thanks,
<Researcher Name / SRE-Degrees project>
*(attach: anonymization_spec.md, anonymization_schema.json)*

---
**Short DM / LinkedIn variant (≤60 words):**
Hi — SRE-Degrees researcher (open incident-response benchmark). Your 2023 kube-proxy outage
postmortem was clear enough that we rebuilt it as a benchmark scenario, with credit. Strictly
reliability incidents, not the security one. Could you review our representation and optionally
share the anonymized timeline/alert-shapes your blog strips out? Spec attached.
