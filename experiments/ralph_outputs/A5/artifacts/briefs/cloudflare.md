# Cloudflare — positioning + contact brief

**Identity:** Global edge network / DNS / security. Gold-standard public postmortem culture and
an established academic/research outreach habit (Cloudflare Research).

## Warm hook (strongest material — 5 scenarios)
We already model FIVE of their public reliability incidents:
- `scenarios/cidg/generated/58-cloudflare-zonemd-stale-cache.yaml` — 2023-10-04 1.1.1.1 ZONEMD stale cache
- `scenarios/cidg/generated/59-cloudflare-byzantine-switch.yaml`
- `scenarios/cidg/generated/60-cloudflare-bgp-reorder.yaml`
- `scenarios/cidg/generated/71-cloudflare-leap-second.yaml`
- `scenarios/cidg/generated/76-cloudflare-waf-regex.yaml`

This depth is the pitch: their postmortems are *so good* they already form a meaningful slice
of our benchmark. Lead by crediting that and offering to let them review the representations.

## What we are already permitted to do (provenance)
All five are publicly published Cloudflare postmortems. We cite each source and model the
failure mechanism only (DNS cache staleness, BGP reordering, leap-second, WAF regex
catastrophic backtracking, switch byzantine fault). No proprietary data.

## Why they'd say yes
- **Cloudflare Research** actively partners with academics; a reliability benchmark is squarely
  in scope.
- Their public-postmortem ethos means "share the structured internals" is a small step from
  what they already publish.

## The ask (least-sensitive useful slice)
The structured internals their blogs strip out — anonymized timeline offsets, alert *shapes*,
remediation order — for incidents already publicly disclosed, in `anonymization_schema.json`
form. **Stretch:** a pointer to a machine-readable postmortem feed if one exists internally.

## Contact path (role-based / public only — VERIFY before sending)
- `[VERIFY]` Cloudflare Research public contact (research.cloudflare.com) — best fit.
- `[VERIFY]` Engineering blog (blog.cloudflare.com) author/team channel.
- `[VERIFY]` Public DevRel / developer-advocacy channel.
- No scraped personal emails; engage public research/DevRel channels only.

## Objection handling
- *"Security sensitivity?"* → Only already-public incidents in v1; failure-mechanism modeling,
  not attack detail; DPA available.
- *"Why us?"* → Your postmortems are the benchmark's backbone; we want to represent you
  accurately and credit you.
- *"Effort?"* → Review our 5 representations, optionally enrich a few via our JSON shape.

## Yield estimate & fallback
**Probability: MEDIUM.** Research-friendly but large org / slow. **Fallback:** their public
postmortems are rich enough to keep using (permitted); seek a blessed-representation + cite
permission from Cloudflare Research.
