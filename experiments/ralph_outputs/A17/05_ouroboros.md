# A17 — Ouroboros: self-critique as 3 different engineers

## Engineer 1 — "Data Provenance Auditor"
**Problem found:** The spec assumes a clean split between "synthetic-leaf" and
"postmortem-derived" by id range, but the registry only has `family ∈ {simple, cascade,
novel}` and `style ∈ {leaf, cascade}`. Those axes do not map 1:1 to provenance. A scenario
can be `family: cascade` yet still postmortem-derived (e.g. GitHub network partition). If
I label provenance purely by registry family I will mislabel.
**Fix:** Derive provenance from `meta.source`: if the source string contains a real
org+date (Facebook, Cloudflare, GitHub, AWS, Azure, Slack, Knight, Datadog, CircleCI,
LaunchDarkly, Mozilla, GitLab) → `postmortem_derived`; else (40–47, 20–22, 30 generic
component templates) → `synthetic_leaf`. Document this heuristic in the card so it is
auditable, and report it as a heuristic, not ground truth.

## Engineer 2 — "Reproducibility Skeptic"
**Problem found:** The card will claim numbers are "reproducible," but `compute_stats.py`
globs a directory whose contents can change (3 unindexed scenarios just appeared). If a
reader runs it next month and gets 38, the card's pasted numbers will silently be stale.
**Fix:** (a) Stamp the card with the exact corpus snapshot (`n_yaml`, `n_registry`, and
the list of unindexed files) and the date. (b) Have `compute_stats.py` print the file
list it counted so a reader can diff. (c) Explicitly say "numbers reflect the corpus as of
<date>; re-run compute_stats.py to refresh." This converts a latent staleness bug into a
documented, regenerable contract.

## Engineer 3 — "Skeptical AAAI Reviewer (round 2)"
**Problem found:** Two over/under-engineering issues. (1) Over: a 9-section datasheet for
35 scenarios risks being longer than the dataset is interesting; reviewers skim. (2) Under:
the *Collection Process* section is the one reviewers scrutinize for contamination, and the
draft plan describes it only abstractly ("postmortem mining → CIDG"). Without naming the
generator and the abstraction step (real incident → synthetic topology + injected fault),
a reviewer can't judge whether solving the sim ≈ solving the real incident.
**Fix:** Keep all sections but make Composition/Limitations dense and tabular (skim-friendly)
and make Collection Process concrete: state that each scenario is a *hand-curated abstraction*
of a public postmortem into the CIDG schema (topology + single hidden root fault + buried
smoking gun + traps), NOT a replay of real telemetry. Explicitly state the construct: the
benchmark tests *root-cause localization under cascading alerts*, and warn this is a
necessary-not-sufficient proxy for real incident response.

## Final filtered spec (deltas applied)
- Provenance split derived from `meta.source` org/date heuristic; documented as a heuristic.
- Card carries a dated corpus snapshot + "re-run compute_stats.py" instruction.
- Collection Process names CIDG, describes the abstraction step, and states the construct
  + its external-validity caveat.
- Composition & Limitations rendered as tables for skimmability.
