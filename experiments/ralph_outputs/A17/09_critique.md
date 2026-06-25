# A17 — Honest Critique

## What a reviewer will attack
1. **Snapshot vs. moving corpus.** The card is dated to a 51-scenario snapshot, but the
   corpus is being actively written by parallel processes and grew under me. A reviewer can
   reasonably say "your numbers are already stale." Mitigation in place (re-run the script),
   but a *published* benchmark must freeze a release commit — that freeze hasn't happened
   here, so the card describes a snapshot of a non-frozen artifact. **Real weakness.**
2. **Provenance split is heuristic, not verified.** The 31/20 postmortem/synthetic split
   comes from string matching on `meta.source`+filename, not a human label per scenario.
   Edge cases (e.g. a synthetic template named after a mechanism that coincidentally contains
   an org substring) could be misclassified. I documented it as a heuristic, but a careful
   reviewer would want a hand-checked label column.
3. **Contamination is flagged, not measured.** I recommend reporting the leaf subset, but I
   did not actually run a model to *demonstrate* a memorization gap between named and
   synthetic scenarios. The contamination claim is a priori, not empirical.
4. **No DOI / external hosting / formal license text.** The card says "governed by the repo
   license" — if the repo lacks an explicit LICENSE file, the licensing section is weaker
   than AAAI artifact-evaluation expects.
5. **Construct validity asserted, not validated.** I state the sim is a "necessary-not-
   sufficient proxy" for real incident response, but there is no study correlating sim score
   with real SRE performance. The card is honest about this, but it remains an unproven gap.
6. **Registry gap is structural.** 19/51 scenarios are unindexed; any registry-driven eval
   silently undercounts. This is arguably a *corpus* bug surfaced by the card, not something
   the card fixes — out of scope per the brief (no shared-core edits), but it limits the
   benchmark's current usability.

## What's missing / could be stronger
- A hand-verified provenance/difficulty label column committed alongside the corpus.
- An empirical contamination probe (leaf vs named pass-rate on one model).
- A frozen release tag + LICENSE reference + a per-scenario `meta.urls` backfill.
- `hysteresis` / `monitoring_degrades` scenarios to exercise the declared-but-unused axes.

## Honest bottom line
The deliverable is a real, reproducible, well-grounded data card that correctly characterizes
the corpus *as it exists right now*, including its warts (registry gap, single platform,
keyword judge, contamination risk, empty URLs). Its main limitation is inherited from the
project state: the corpus is unfrozen and the registry lags, so the card documents a moving
target rather than a sealed release. That's the right, honest thing to ship at this stage.
