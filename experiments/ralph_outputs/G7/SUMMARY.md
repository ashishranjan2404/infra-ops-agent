# G7 — Summary

**Task:** Track Resolve.ai (closest commercial AI-SRE competitor). Produce a cited competitor
tracking brief + a structured watch-list; be honest about what is publicly knowable.

## Deliverables (all under experiments/ralph_outputs/G7/)
- artifacts/resolve_ai_competitor_brief.md — source-cited brief ([S1]-[S10]); all self-reported
  metrics tagged (vendor-reported); explicit "NOT publicly knowable" section.
- artifacts/resolve_ai_watchlist.yaml — 8-item structured watch-list (what / where / signal /
  cadence / verifiability / why_it_matters) + 8 not-knowable entries.
- artifacts/validate_watchlist.py — schema validator; runs clean (OK: 8 watch items, schema valid).
- 01-10 cycle files + this SUMMARY + result.json.

## Key findings (as-of 2026-06-25)
- Resolve AI: founded early 2024 by Spiros Xanthos (CEO) + Mayank Agarwal (CTO), SF; both
  OpenTelemetry co-creators, ex-Splunk Observability leaders.
- $125M Series A led by Lightspeed at $1B valuation (2026-02-04); total raised >$150M.
- Positioning: vendor-neutral "AI Production Engineer / AI SRE" over existing observability/code/infra
  (Datadog, Grafana, GitHub, Jenkins, Slack).
- 2026-05-21 launch: always-on agents + multi-agent parallel-hypothesis investigation architecture,
  claimed >2x root-cause accuracy, REST API + MCP server.
- Customers (vendor-reported): Coinbase 72% faster critical-incident investigation; DoorDash up to 87%
  faster time-to-root-cause; ~5-min triage. Logos: Coinbase, DoorDash, MongoDB, MSCI, Salesforce, Zscaler.

## Honesty boundary
Pricing, true accuracy methodology, model/provider stack, real agent topology, revenue/churn,
paying-customer count, and failure modes are NOT public - enumerated explicitly, not invented.

## Tests
4/4 pass: validator (exit 0), YAML parse, brief section structure, vendor-tagging + source count.

## Containment
No shared core files edited; all output is task-namespaced under G7/.
