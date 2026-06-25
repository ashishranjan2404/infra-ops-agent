# A17 — Improved Plan (post-grill)

## What changed vs. 01_plan.md

### Accepted critiques
- **(AR) Add a dedicated Contamination Risk section.** Scenarios 50–82 carry real
  postmortem titles/dates (Facebook BGP, Cloudflare WAF, Knight Capital, Cloudbleed…)
  that frontier LLMs have likely read. The card now warns that scores on *named* scenarios
  may reflect memorization, and recommends reporting the synthetic-leaf subset separately.
- **(SMR) Split composition by provenance class.** Add a table breaking the 35 scenarios
  into `synthetic-leaf` vs `postmortem-derived`, so a contamination-controlled subset is
  computable. Drive this from `registry.json` `family`/`style` + id ranges.
- **(PS) Quantify the thesis.** Report `cascades` (27/35) and `buried_gun_exists` (27/35)
  counts as first-class composition stats — they are the construct under test.
- **(RLE + PS) Document the scoring contract *and* its threats.** Add a "How items are
  scored" subsection: deterministic keyword judge over `gold_root`/`red_herrings` is the
  reproducible default; note (a) keyword-hacking / paraphrase fragility and (b) that the
  `default_judge` LLM fallback breaks determinism — so reproducible numbers require the
  deterministic/hybrid judge.
- **(DL) Frame sim+seed as a reproducibility trade-off.** State the determinism guarantee
  (per-scenario `seed`, deterministic sim) and the regeneration path, framed as
  external-validity↓ / reproducibility↑, not merely an apology.
- **(SMR/DL) Honest gaps.** Document empty `meta.urls` and the registry(32)/disk(35)
  mismatch (scenarios 80/81/82 not yet indexed).

### Rejected / deferred critiques
- **(PS) "Replace the keyword judge."** Out of scope for a *data card* — the card
  documents and warns about the judge; changing it is a separate task. Rejected here.
- **(AR) "Scores on named scenarios are worthless."** Too strong. Per SMR, the leaf subset
  is contamination-safe and the postmortem set still tests *diagnosis under a different
  simulated topology* than the real incident. We flag risk, not invalidity. Rejected as
  stated; softened into a recommendation to report subsets.

## Final deliverable shape
`DATA_CARD.md` with sections:
1. Motivation
2. Composition (with provenance-class split + thesis stats, all machine-derived)
3. Collection Process (postmortem mining → CIDG generation → sim encoding)
4. Preprocessing / Labeling (gold_root, red_herrings, smoking guns, traps)
5. Uses (RL training, eval, ablations) + How items are scored (judge contract + threats)
6. Distribution & Licensing
7. Maintenance
8. Reproducibility Appendix (schema, determinism, regeneration, registry gap, contamination)

Supporting: `compute_stats.py` (re-derives all numbers), `stats.json` (its output).
