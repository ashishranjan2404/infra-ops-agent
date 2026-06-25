# G7 — 01 Plan

## Objective
Stand up a repeatable competitor-tracking capability for **Resolve.ai** — the closest
commercial competitor to the SRE-Degrees / REx AI-SRE work in this repo. Deliverables:
1. A factual, source-cited **competitor tracking brief** on Resolve.ai's current product and positioning.
2. A structured, machine-readable **watch-list** (what to monitor, where, how often) so the brief
   can be re-run / updated over time rather than being a one-shot snapshot.
3. Honesty about the boundary between what is *publicly knowable* and what is *not*.

This is a **research + intelligence** task, not a code-on-the-cluster task. The "artifact" is a
durable, validated knowledge asset (a YAML watch-list + a markdown brief) that a human or a future
agent can act on.

## Approach
- Fan-out web search across: company/funding, product pages, the most recent product-launch press
  release, founder/leadership background, integrations/ecosystem, and third-party comparisons.
- Prefer **primary sources** (resolve.ai, their PR Newswire releases, investor blog posts from
  Lightspeed/Greylock) and corroborate dated claims (funding, accuracy numbers) with at least one
  independent outlet (TechCrunch, Bloomberg, PYMNTS).
- Separate **claims-with-numbers** (which must be cited and dated) from **interpretation**.
- Encode the recurring monitoring plan as a YAML watch-list with explicit sources, signals, and
  cadence so it is re-runnable.

## Files to create (all task-namespaced under G7/)
- `01_plan.md` … `10_feedback.md` (the 10 cycle files)
- `SUMMARY.md`, `result.json`
- `artifacts/resolve_ai_competitor_brief.md` — the human-readable brief (primary deliverable)
- `artifacts/resolve_ai_watchlist.yaml` — structured watch-list (machine-readable deliverable)
- `artifacts/validate_watchlist.py` — tiny validator (YAML parse + schema check) so the artifact
  is provably valid, not placeholder.

## Dependencies
- Web search / fetch tools (used). No cluster, no GPU, no live API keys required.
- `pyyaml` for the validator (already a repo dep per `requirements-rex.txt`).

## Risks
- **Recency/decay**: competitive intel rots fast. Mitigation: watch-list with cadence + "as-of" date stamps.
- **Marketing vs. reality**: vendor accuracy claims ("2x", "87%") are self-reported. Mitigation: label them as vendor-reported and cite source + customer.
- **Hallucinated specifics**: pricing, exact integration counts, internal architecture are largely
  non-public. Mitigation: an explicit "what is NOT publicly knowable" section; do not invent.

## Success criteria
1. Brief covers: company/funding, positioning, product capabilities, architecture, ecosystem,
   customers/metrics, leadership — every hard claim carries a source URL.
2. Watch-list is valid YAML, parses, and passes a schema check; has ≥5 watch items each with
   source + signal + cadence.
3. A clearly delimited "publicly knowable vs. not" section exists and is honest.
4. No shared core files edited; all artifacts live under `G7/`.
