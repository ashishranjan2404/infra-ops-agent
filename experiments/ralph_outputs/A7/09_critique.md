# A7 — 09 Critique (honest)

## The headline weakness
`expected_pass_rate` is an **uncalibrated prior**, not a measured rate. There
are no labelled agent pass rates in the CIDG corpus, so the absolute numbers
(0.43–0.87) cannot be validated against reality. A reviewer is right to treat
them as *ordinal* (use the ranking / buckets) and not as a benchmark to plot
against measured pass@1. This is the single biggest attack surface and I do not
paper over it.

## Other weaknesses a reviewer would hit
- **Low-variance inputs.** Across the corpus, `severity` is ~always 0.7 and
  `flap_prob` ~0.05, so those terms contribute a near-constant offset and ~zero
  discrimination. They survive only as future-proofing.
- **Bimodal corpus.** The set is essentially two clusters: synthetic single-node
  "leaf" incidents (epr 0.87) and multi-node postmortems (epr ~0.43). The fine
  within-cluster ordering exists but is driven by small topology/buried-depth
  deltas; its resolution is real but modest.
- **Hand-set weights & thresholds.** The 0.16/0.12/… weights and 0.70/0.45
  bucket cuts are reasoned, not learned. Different reasonable weights would
  reshuffle mid-pack incidents. Mitigated by shipping the full breakdown so the
  weighting can be contested/retuned, but it is still a judgement call.
- **Floor compression.** Because base=0.92 and the trap cap is 0.55, epr can't
  fall below ~0.37, so the hardest incidents look "only" ~0.43. The scale is
  compressed at the hard end; bucket boundaries partly compensate.

## What's missing / future work
- **Calibration:** once `rex/eval_pass_at_k.py` produces real per-incident
  pass@1 over a model set, fit/validate the prior against it (e.g. isotonic
  regression on trap_complexity → observed pass rate). This is the right way to
  earn the name `expected_pass_rate`.
- **Consumption wiring:** surfacing `difficulty_bucket` in the eval harness for
  stratified reporting was intentionally NOT done (parallel-safety: no edits to
  shared core .py). Filed as a follow-up patch.

## Net honest assessment
Solid, reproducible, auditable, non-mutating ordinal difficulty labelling that
unblocks stratified eval and curriculum sampling **today**. It is explicitly
NOT a calibrated probability and should not be reported as one until validated
against measured outcomes.
