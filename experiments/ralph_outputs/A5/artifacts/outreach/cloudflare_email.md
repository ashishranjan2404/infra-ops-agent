# Cloudflare — outreach draft

**To:** `[VERIFY]` Cloudflare Research / Engineering blog team
**Subject:** Five of your postmortems are the backbone of our SRE benchmark — review + go deeper?

Hi Cloudflare Research team,

I'm a researcher on SRE-Degrees, an open benchmark for training and evaluating incident-response
agents. Your postmortems are good enough that five of them already form a meaningful slice of
our scenario set — the 2023-10-04 1.1.1.1 ZONEMD stale-cache event, the BGP-reorder incident,
the leap-second event, the WAF regex catastrophic-backtracking incident, and a byzantine-switch
fault. We model only the *failure mechanism* from your public writeups, cite each source, and use
no proprietary data. We'd love to have you review how you're represented.

Two asks, either is a win:

1. A short call (or async review) of our five representations, with permission to cite that
   Cloudflare Research reviewed them.
2. (Optional) Sharing the structured internals your blogs strip out for those already-public
   incidents — anonymized timeline offsets, alert *shapes* (signal + threshold relation + unit,
   no values), and remediation order — in the JSON shape in the attached spec. v1 only touches
   already-public incidents; a DPA is fine for anything beyond.

Given Cloudflare Research's academic-collaboration track record, I'm hopeful this is squarely in
scope. Even just a blessed representation + cite permission would be valuable.

Thanks for setting the bar on public postmortems,
<Researcher Name / SRE-Degrees project>
*(attach: anonymization_spec.md, anonymization_schema.json)*

---
**Short DM / LinkedIn variant (≤60 words):**
Hi — SRE-Degrees researcher. Five Cloudflare postmortems (ZONEMD, BGP reorder, leap-second, WAF
regex, byzantine switch) are the backbone of our open incident benchmark; we model the failure
mechanism only and cite you. Could Cloudflare Research review our representations, and would you
consider sharing the anonymized timeline/alert-shapes your blogs strip out? Spec attached.
