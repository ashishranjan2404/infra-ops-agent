# F5 — Implementation

## What I built
A single deliverable artifact: a tightened, AAAI-ready abstract that replaces the loose
~230-word draft in `PAPER_OUTLINE.md` §Abstract (lines 9–27), grounded in the *honest*
measured results rather than the outline's aspirational phrasing.

- **Artifact:** `experiments/ralph_outputs/F5/artifacts/abstract.md`
  - `# Abstract` heading (uncounted)
  - one 233-word abstract paragraph (the counted body)
  - `---` rule
  - `**Word count: 233**` line
  - `## Provenance` appendix mapping every quantitative claim → its source artifact,
    plus an explicit list of what was *omitted as unsupported*.

## Key authoring decisions (traceable to the grill + ouroboros)
1. **Relocated the headline** from the REx refinement loop to the *verifiable
   environment + learned verifier*, per `headline_insights.md` §3 (grill R3, ouroboros B).
2. **Honest numbers, no false precision:** used the insight-doc pair (~0.90 vs 0.95
   hand-written, 14→3 rules, one unseen-hazard miss) instead of the outline's
   2-decimal 89.7/94.9 on n=3 held-out incidents.
3. **REx lift stated honestly with its boundary:** 0.69 vs 0.24 zero-shot, but
   collapses to 0.25 with the oracle hint stripped — grounded in the *verified*
   `rex/runs/ablation.json` aggregate (rex 0.687 / zero_shot 0.242 / rex_no_oracle 0.250).
4. **Omitted unsupported claims:** C2 FIREBALL transfer (pending) and any McNemar
   p-value (grid partly pending) are deliberately absent; documented in Provenance.

## Shared-core safety
No shared core files were edited. `PAPER_OUTLINE.md` was READ ONLY. The improved abstract
lives entirely under `experiments/ralph_outputs/F5/`. If adopted, a maintainer can copy
the artifact body into the outline — that edit is left to a human, not made by this worker.

## Verification of grounding (run, not assumed)
- `python3` read of `rex/runs/ablation.json` confirmed the five arms and the aggregate
  means cited above (see 07).
- `wc -w` over the body confirmed 233 words ≤ 250.
