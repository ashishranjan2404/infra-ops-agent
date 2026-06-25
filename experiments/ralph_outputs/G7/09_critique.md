# G7 — 09 Critique (honest)

## What's weak / where a reviewer attacks
1. **Single-pass research, no longitudinal data.** This is one snapshot. The whole *value* of competitor
   tracking is the time series, and I produced t=0 only. The watch-list makes it *re-runnable* but I did
   not actually re-run it or stand up polling — so the "tracking" is currently aspirational, not operating.
2. **Source concentration on the vendor.** Despite dual-sourcing funding, most *product* detail (capabilities,
   architecture, integrations) comes from Resolve's own pages/press. There is little independent technical
   review or hands-on testing in public, so the product section is inherently vendor-skewed. I labeled it,
   but labeling doesn't remove the bias.
3. **Metrics are uncheckable.** "72%", "87%", ">2x", "<1 minute" are all self-reported with no denominators,
   methodology, or third-party audit. A skeptical reviewer discounts all of them to ~zero evidentiary weight.
4. **No live verification of source URLs in the YAML.** Some `where` URLs (e.g. `/customers`, the PitchBook
   profile, founder X handle) are plausible/standard but I did not 200-check every one; a couple could be
   dead or gated, which would silently degrade the poller.
5. **REx-relevance is thin by design.** I deliberately avoided over-claiming a head-to-head, but that means
   the "so what for us" payload is qualitative. There is no benchmark parity, so strategic conclusions are soft.
6. **Recency cliff.** As-of 2026-06-25. The May-2026 launch is the freshest hard event; anything they shipped
   in June is likely missed. The brief decays fast.

## What's missing
- A competitive matrix vs. other AI-SRE entrants (Datadog Bits AI, Sherlocks.ai, incident.io AI, Cleric, etc.).
- Pricing intelligence (genuinely non-public, but even anecdotal/sales-call signal would help).
- Any independent benchmark or our own eval of their public demo.
- An actual scheduled job consuming the watch-list.

## Honest status of blocked/negative results
- **Not blocked**: all intended deliverables (brief + watch-list + validator) are real and validated.
- **Honestly negative**: I cannot verify a single one of their accuracy claims, cannot get pricing, and
  cannot confirm internal architecture. These are stated as unknowable rather than papered over — which is
  the correct outcome for this task, but it does cap how "actionable" the intel can be.
