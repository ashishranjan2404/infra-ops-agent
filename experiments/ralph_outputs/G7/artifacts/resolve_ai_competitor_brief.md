# Competitor Tracking Brief — Resolve.ai (Resolve AI, Inc.)

**As-of:** 2026-06-25
**Scope:** Closest commercial competitor to the SRE-Degrees / REx AI-SRE work. Covers public
product, positioning, funding, ecosystem, and proof points. **Every hard claim below is cited;
self-reported metrics are tagged `(vendor-reported)`.**

**One-line:** Resolve AI is a venture-backed, vendor-neutral "AI Production Engineer / AI SRE"
that runs a multi-agent investigation layer on top of a company's existing observability, code, and
infra tooling to triage alerts and find root cause; it reached a $1B valuation on a $125M Series A
in Feb 2026 and shipped "always-on agents" + a new investigation architecture in May 2026.

---

## Company & funding
- **Founded:** early 2024 by **Spiros Xanthos** (CEO) and **Mayank Agarwal** (CTO); HQ **San Francisco**. [S7][S9]
- **Series A:** **$125M**, led by **Lightspeed Venture Partners**, with Greylock, Unusual Ventures, and A*; announced **Feb 4, 2026**. [S1][S2]
- **Valuation:** **$1B** (unicorn) on the Series A; total funding **>$150M**. [S2][S6] Corroborated independently by TechCrunch and Bloomberg. [S2][S10]

## Positioning
- Markets itself as **"AI for prod"** / an **"AI Production Engineer"** and, more narrowly, an **AI SRE**
  that resolves alerts and incidents. [S3][S4][S5]
- Key strategic stance: a **vendor-neutral layer** that sits on top of existing observability, infra,
  and code tools rather than being tied to one platform. [S3] (This is the wedge against incumbents like
  Datadog Bits AI, which are tied to their own data plane.)

## Product capabilities (stated)
- On alert, **immediately investigates**: reviews metrics, dashboards, code changes, deployments, and
  logs; **autonomously creates and executes just-in-time runbooks**; claims a root-cause theory in
  **under a minute**. [S4]
- **Always-on background agents** that continuously perform operational work (announced May 21, 2026). [S8]
- **Collaborative investigation surface**: engineers and agents work over the same live evidence; reports
  update dynamically; findings are inspectable; source queries are pullable/modifiable in place; structured
  explanations with **citations** showing reasoning, queries, and the specific PRs that introduced problems. [S8][S4]
- Programmatic surface: **REST API** and an **MCP server** integration option (May 2026). [S8]

## Architecture (stated claims — **unverified**, vendor-reported)
- A **multi-agent investigation architecture**: a coordinated team of specialized agents investigates
  **multiple hypotheses and evidence sources in parallel**, independently verifying conclusions. [S8]
- Claimed **>2x improvement in root-cause accuracy** vs. earlier versions (May 21, 2026 launch). `(vendor-reported)` [S8]
- *Note:* internal model stack, prompting, and the actual agent topology are **not public**; the above is
  Resolve's own description and has not been independently verified.

## Ecosystem & integrations
- Connects to observability (**Grafana, Datadog**), CI/CD (**Jenkins**), and code (**GitHub**). [S3]
- Loop-in via **Slack @mentions** or the Resolve UI. [S3]
- Positioned explicitly as cross-stack / vendor-neutral rather than locked to a single observability vendor. [S3]

## Customers & metrics (each `vendor-reported`, customer named)
- Named users include **Coinbase, DoorDash, MongoDB, MSCI, Salesforce, Zscaler**. [S1][S8]
- **Coinbase:** **72% reduction in time to investigate critical incidents** `(vendor-reported)`. [S1]
- **DoorDash:** **up to 87% reduction in time to root cause** `(vendor-reported)`. [S8]
- Agents typically **triage alerts within ~5 minutes** `(vendor-reported)`. [S8]
- *Caveat:* all metrics are self-reported by Resolve; denominators/methodology are not published.

## Leadership
- **Spiros Xanthos** and **Mayank Agarwal** are **co-creators of OpenTelemetry**; previously built
  companies acquired by **Splunk** (Omnition, 2019) and **VMware**; most recently led **Splunk
  Observability** as GM and Chief Architect respectively. [S7][S9]

## Relevance to SRE-Degrees / REx (qualitative — **we have NOT benchmarked against them**)
- Same problem space (autonomous incident investigation / root-cause), but Resolve is a **deployed
  commercial product on real customer telemetry**, whereas REx in this repo is a **research harness**
  (Thompson-sampling refinement tree, deterministic judge, synthetic + HUD scenarios).
- Their public differentiators worth internalizing: **vendor-neutral data access**, **just-in-time
  runbooks**, **parallel multi-hypothesis verification**, and **citation-backed reports** (inspectable
  evidence + offending PRs). These map to evaluation axes we could adopt (evidence-citation quality,
  multi-hypothesis spread), but no head-to-head accuracy comparison exists or is claimed here.

## What is NOT publicly knowable
- **Pricing** — no public price list or tiers.
- **True accuracy / methodology** — only relative ("2x", "87%") self-reported numbers; no benchmark,
  denominator, or eval protocol published.
- **Model/provider stack** — which foundation models, fine-tuning, or orchestration framework.
- **Real agent topology** — beyond "coordinated specialized agents in parallel."
- **Retention / churn / revenue / ARR**, **paying-customer count vs. logos shown**, and **headcount specifics**.
- **Failure modes / false-positive rate** in production.

## Sources
- [S1] Resolve AI — Series A blog: https://resolve.ai/blog/series-a-funding
- [S2] TechCrunch — $125M raise, unicorn valuation (2026-02-04): https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/
- [S3] Resolve AI — product deep dive (AI Production Engineer): https://resolve.ai/blog/product-deep-dive
- [S4] Resolve AI — AI SRE product page: https://resolve.ai/product/ai-sre
- [S5] Resolve AI — "What is an AI SRE?": https://resolve.ai/glossary/what-is-ai-sre
- [S6] FinSMEs — Series A at $1B valuation: https://www.finsmes.com/2026/02/resolve-ai-raises-125m-in-series-a-funding-at-1b-valuation.html
- [S7] Resolve AI — About: https://resolve.ai/about-us
- [S8] PR Newswire — Always-on agents + new investigation architecture (2026-05-21): https://www.prnewswire.com/news-releases/resolve-ai-expands-platform-with-always-on-agents-and-new-investigation-architecture-302778310.html
- [S9] Greylock — "How Resolve AI is building agents...": https://greylock.com/greymatter/how-resolve-ai-is-building-agents-to-keep-the-worlds-software-running/
- [S10] Bloomberg — Resolve AI hits $1B valuation (2026-02-04): https://www.bloomberg.com/news/articles/2026-02-04/resolve-ai-hits-1-billion-valuation-for-outage-thwarting-ai-agents
