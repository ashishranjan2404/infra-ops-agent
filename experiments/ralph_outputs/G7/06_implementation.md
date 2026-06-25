# G7 — 06 Implementation

## What I built (real artifacts, all under G7/, no shared core files touched)
1. **`artifacts/resolve_ai_competitor_brief.md`** — cited competitor brief. 11 sections; every hard
   claim carries an inline source ref `[S#]` resolvable in the Sources list; all self-reported metrics
   tagged `(vendor-reported)` with the customer named; explicit "NOT publicly knowable" section.
2. **`artifacts/resolve_ai_watchlist.yaml`** — structured, machine-readable watch-list. `meta` block,
   **8 watch items** (≥7 required) each with `id/what/where/signal/cadence/verifiability/why_it_matters`,
   plus an 8-entry `not_publicly_knowable` list. `verifiability` field carries the epistemics
   (high/medium/low) per the grill consensus.
3. **`artifacts/validate_watchlist.py`** — schema validator (yaml.safe_load + field/enum/length checks).
   Prints offending `id`/key on failure; prints `OK: …` and exits 0 on success.

## Research method
Fan-out web search + targeted fetch of the primary May-2026 PR Newswire launch release. Funding/valuation
dual-sourced (Resolve blog + TechCrunch + Bloomberg). Founder/leadership from Resolve About + Greylock.
Integrations from the Resolve product deep-dive. See Sources [S1]–[S10] in the brief.

## Key facts captured (with dates)
- Founded early 2024 by Spiros Xanthos (CEO) + Mayank Agarwal (CTO), SF; both co-creators of OpenTelemetry, ex-Splunk Observability leaders.
- Series A: $125M led by Lightspeed, $1B valuation, announced 2026-02-04; total raised >$150M.
- 2026-05-21: "always-on agents" + new multi-agent investigation architecture; claimed >2x root-cause accuracy; REST API + MCP server.
- Customers (vendor-reported metrics, customer-named): Coinbase 72% faster critical-incident investigation; DoorDash up to 87% faster time-to-root-cause; ~5-min triage.
- Positioning: vendor-neutral "AI for prod" / "AI Production Engineer" / AI SRE on top of Datadog/Grafana/GitHub/Jenkins/Slack.

## Honesty boundary (per task requirement)
Pricing, true accuracy methodology, model stack, real agent topology, revenue/churn, paying-customer
count, and failure modes are all **not public** and are enumerated as such in both artifacts.

## Proposed change to shared core (NOT applied)
None required. This task is a standalone intel asset; the watch-list YAML is poll-ready so a future
cron/agent could consume it, but I did not wire any shared scheduler or edit any `rex/*`, `sim/*`,
`agent/*`, or `experiments/*.py` file.
