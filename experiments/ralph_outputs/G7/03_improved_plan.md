# G7 — 03 Improved Plan

## What changed after the grill
1. **Split deliverable into snapshot + policy.** Brief = the cached snapshot; YAML watch-list = the
   re-runnable monitoring policy. (RLE's point, accepted.)
2. **Provenance mandatory + vendor tagging.** Every numeric/factual claim carries a source URL;
   self-reported metrics labeled `vendor-reported` with the customer named. (REV, accepted.)
3. **Epistemics moved into structure.** Watch-list items gain a `verifiability` field (high/medium/low)
   instead of leaving honesty to prose. (RLE+REV, accepted.)
4. **Architecture reframed.** Their multi-agent / hypothesis-verification design is documented as
   *"stated claims, unverified,"* not as analysis we can stand behind. (SMR concedes to PSRE, accepted.)
5. **Track launch *direction*, not just numbers.** PR cadence/topic is a roadmap signal worth tracking
   even when the numbers are soft. (DOL, accepted.)
6. **Explicit "NOT publicly knowable" section.** (Consensus.)

## Critiques accepted
- REV's provenance discipline → adopted as a hard rule.
- RLE's "structure carries epistemics" → added `verifiability` + `vendor_reported` flags.
- PSRE's "don't reverse-engineer an unverifiable architecture" → architecture demoted to stated-claims.

## Critiques rejected (and why)
- SMR's original "deeply map their agent graph onto REx": **rejected** — their internal architecture
  is one PR sentence; a detailed mapping would be fabrication. Kept only a short, labeled comparison
  of *publicly stated* approach vs. REx's *publicly visible* approach (this repo).
- A pure live-poller with no human cache (implied by an aggressive RLE reading): **rejected** as
  out of scope for one task; instead the watch-list is structured so a future cron/agent *could*
  poll it, but I do not stand up live polling here.

## Revised success criteria (unchanged targets, sharper)
- Brief: ≥7 sections, every hard claim cited, vendor numbers tagged, "not knowable" section present.
- Watch-list: valid YAML, ≥7 items, each with `source`, `signal`, `cadence`, `verifiability`; passes validator.
- Validator script runs clean (exit 0) and is included as proof.
