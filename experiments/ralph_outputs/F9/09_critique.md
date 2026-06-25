# 09 — Honest critique

## What's weak
- **Provenance is thin.** 40/51 incidents carry `source == "Synthetic simple incident
  (...)"` with empty `urls`. The catalog faithfully reports this, but a skeptical
  reviewer will note that the "incident catalog" is majority synthetic and only a
  minority (the named ones: github-*, cloudflare-*, slack-*, aws-*, etc.) are grounded
  in real public postmortems. The catalog surfaces the mix in the Summary, but it
  cannot manufacture realism that isn't in the specs.
- **`source` duplicates `title`** for the synthetic specs (both are the same string).
  That's an upstream generator artifact, not something this catalog should paper over.
- **No URL grounding for the real-named incidents either.** The named specs reference
  real outages by title (e.g. "GitHub 2018-10-21 network partition") but their
  `urls: []` is empty in the YAML, so the catalog has no clickable citations to show.
  Fixing that means editing the source YAMLs (a shared-core change, out of scope here).
- **Severity is uniformly 0.7** across most specs — a reviewer may question whether
  severity is a meaningful axis or just a constant. The catalog reports it but cannot
  fix the underlying lack of variance.

## What a reviewer attacks
- "Your supplementary catalog proves the substrate is mostly synthetic." — True; we
  report it honestly rather than hide it. The defense is that the synthetic specs are
  parametric (failure-class generators) and the named ones provide real grounding.
- "Fix column is just the canonical_fix tool — is that the only valid remediation?"
  — The catalog reflects the single canonical fix the harness rewards; it does not
  enumerate alternative valid fixes (the specs don't encode them).

## What's missing
- Cross-links from each incident to the harness/judge that consumes it.
- A column for `slo` targets and `trap_actions` (the distractor actions) — would make
  the catalog more useful for analyzing reward-hacking, but was scoped out to keep the
  table readable.

## Honest bottom line
The deliverable is real, correct, and regenerable, and it tells the truth about the
substrate (synthetic-heavy, uniform severity). Its limits are inherited from the
source specs, not from the generator. To strengthen grounding, the upstream YAMLs
would need real postmortem URLs added — a shared-core change deliberately not made.
