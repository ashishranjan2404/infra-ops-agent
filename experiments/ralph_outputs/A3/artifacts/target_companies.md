# Target list — sourcing 10+ fully real incidents

Goal: get **10+ first-party donated incidents** with the cascade shape (loud victim symptom,
trap action that worsened it, correct fix). Two tracks. Aim ~3-4x oversubscription on the
volume track (community donors are flaky) and 2-3 signed donors on the DUA track.

Columns: **track** (community_warm | dua_nonpublic), **reachability** (warm | cold),
**expected_provenance**, **rationale**.

## Track 1 — community_warm (high volume, flaky, often already-public)

| # | Target | reachability | expected_provenance | Rationale |
|---|--------|--------------|---------------------|-----------|
| 1 | incident.io Slack community | warm | first_party_donated | Project already cites their anetd/cilium postmortem (spec 03); incident-tooling company with a public incident culture; existing relationship. Highest-yield warm node. |
| 2 | SREcon (USENIX) attendee network | warm | first_party_donated | Practitioners who *live* cascading outages; a CFC posted to the SREcon Slack/mailing list reaches hundreds of SREs. |
| 3 | r/sre + r/kubernetes (Reddit) | cold | first_party_donated | Volume channel; SREs love war stories. Skews public but yields raw first-person timelines. |
| 4 | rootly / FireHydrant communities | warm | first_party_donated | Incident-management vendors with engaged user Slacks; same cultural fit as incident.io. |
| 5 | CNCF #kubernetes-users / #sig-network Slack | cold | first_party_donated | Where the K8s networking cascades (CNI, kube-proxy, Cilium) actually get debugged in public. |
| 6 | k8s "failure stories" (k8s.af) maintainers | cold | public_postmortem | Curated K8s failure list; warm intro to the curators can surface contributors. |
| 7 | The Pragmatic Engineer / SRE Weekly readers | cold | first_party_donated | Newsletter audience of senior infra eng; a sponsored CFC blurb reaches the exact demographic. |
| 8 | Honeycomb / observability vendor dev-rel | warm | first_party_donated | Observability orgs publish detailed incident write-ups and have war-story-friendly cultures. |
| 9 | PagerDuty community + "Postmortem" Slack groups | cold | first_party_donated | On-call practitioners; trap-action stories are common. |
| 10 | Personal/professional SRE network (project authors) | warm | first_party_nonpublic | Direct asks to ex-colleagues yield the *non-public* incidents that carry the novelty claim. |
| 11 | HUD community / RL-env builders | warm | first_party_donated | Already adjacent to this project; some run real infra and can donate. |

## Track 2 — dua_nonpublic (low volume, slow, human/legal-gated, carries novelty)

| # | Target | reachability | expected_provenance | Rationale |
|---|--------|--------------|---------------------|-----------|
| 12 | incident.io (company, not just community) | warm | first_party_nonpublic | Best DUA candidate: incident data *is* their product; a light DUA for de-identified, unpublished incidents is plausible given the existing relationship. |
| 13 | A mid-size SaaS with a friendly VP-Eng contact | warm | first_party_nonpublic | One internal sponsor + a 1-page DUA can release de-identified incidents not on any blog. The realistic source of genuinely-novel data. |
| 14 | Cloud-native startups (Series B/C) | cold | first_party_nonpublic | Smaller orgs move faster on a light DUA than FAANG; offer the graded scenario back as the incentive. |
| 15 | University SRE / research-infra teams | cold | first_party_nonpublic | Research-friendly, lower legal friction, real but unpublished cluster cascades. |
| 16 | Managed-K8s / platform vendors (e.g. via dev-rel) | warm | first_party_nonpublic | They see many customers' cascades; a sanitized, aggregated donation under DUA is feasible. |

## Reachability notes (honesty)
- **Cold FAANG SRE orgs are deliberately excluded** — historic ~0% yield, heavy legal,
  long cycles. Public postmortems already cover them (the existing 19 specs).
- The **DUA track is human- and lawyer-gated**; an autonomous agent cannot sign or negotiate.
  Realistic near-term yield is the community_warm track; DUA track is the slower, higher-value
  follow-up that secures the "fully real / non-public" provenance claim.
- Expected funnel to hit 10+: contact ~30 across tracks → ~10 reply → ~10-12 usable incidents
  (community) + 2-3 (DUA). Oversubscribe accordingly.
